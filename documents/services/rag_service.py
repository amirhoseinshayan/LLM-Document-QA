from dataclasses import dataclass

from documents.models import Document, QuestionAnswer
from documents.services.llm_service import generate_answer_from_context
from documents.services.search_service import search_relevant_chunks


@dataclass
class RAGAnswerResult:
    """
    Store the final RAG answer result.
    """
    question: str
    answer: str
    used_chunks: list
    related_documents: list[Document]
    history: QuestionAnswer


def build_context_from_search_results(search_results) -> str:
    """
    Build a single context string from retrieved chunks.
    """
    context_parts = []

    for index, result in enumerate(search_results, start=1):
        chunk = result.chunk

        context_parts.append(
            (
                f"[Chunk {index}]\n"
                f"Document: {chunk.document.title}\n"
                f"Chunk index: {chunk.chunk_index}\n"
                f"Content:\n{chunk.content}"
            )
        )

    return "\n\n---\n\n".join(context_parts)


def get_unique_related_documents(search_results) -> list[Document]:
    """
    Extract unique related documents from search results.
    """
    documents = []
    seen_document_ids = set()

    for result in search_results:
        document = result.chunk.document

        if document.id not in seen_document_ids:
            documents.append(document)
            seen_document_ids.add(document.id)

    return documents


def answer_question_with_rag(
    question: str,
    top_k: int = 5,
    document_id: int | None = None,
) -> RAGAnswerResult:
    """
    Retrieve relevant chunks, generate an answer, and store the question-answer history.
    """
    search_results = search_relevant_chunks(
        query=question,
        top_k=top_k,
        document_id=document_id,
    )

    related_documents = get_unique_related_documents(search_results)

    if not search_results:
        answer = "The provided documents do not contain enough information to answer this question."
    else:
        context = build_context_from_search_results(search_results)
        answer = generate_answer_from_context(
            question=question,
            context=context,
        )

    history = QuestionAnswer.objects.create(
        question=question,
        answer=answer,
    )

    if related_documents:
        history.related_documents.set(related_documents)

    return RAGAnswerResult(
        question=question,
        answer=answer,
        used_chunks=[result.chunk for result in search_results],
        related_documents=related_documents,
        history=history,
    )
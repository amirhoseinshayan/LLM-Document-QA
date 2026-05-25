from dataclasses import dataclass

from documents.models import QuestionAnswer
from documents.services.llm_service import generate_answer
from documents.services.search_service import search_relevant_chunks


@dataclass
class RAGResult:
    """
    Result object returned by the RAG pipeline.
    """

    question: str
    answer: str
    used_chunks: list
    related_documents: list
    history: QuestionAnswer
    llm_provider: str
    llm_model: str
    used_fallback: bool


def build_context_from_search_results(search_results) -> str:
    """
    Build a context string from retrieved chunks.
    """
    context_parts = []

    for index, result in enumerate(search_results, start=1):
        chunk = result.chunk
        context_parts.append(
            f"[Chunk {index} | Document: {chunk.document.title}]\n"
            f"{chunk.content}"
        )

    return "\n\n".join(context_parts)


def get_unique_related_documents(search_results) -> list:
    """
    Return unique related documents from search results.
    """
    documents = []
    seen_ids = set()

    for result in search_results:
        document = result.chunk.document

        if document.id not in seen_ids:
            documents.append(document)
            seen_ids.add(document.id)

    return documents


def answer_question_with_rag(question: str, top_k: int = 5, document_id=None) -> RAGResult:
    """
    Retrieve relevant chunks, generate an answer, and save the history record.
    """
    search_results = search_relevant_chunks(
        query=question,
        top_k=top_k,
        document_id=document_id,
    )

    context = build_context_from_search_results(search_results)
    llm_result = generate_answer(question=question, context=context)
    answer = llm_result.answer
    related_documents = get_unique_related_documents(search_results)

    history = QuestionAnswer.objects.create(
        question=question,
        answer=answer,
    )
    history.related_documents.set(related_documents)

    return RAGResult(
        question=question,
        answer=answer,
        used_chunks=[result.chunk for result in search_results],
        related_documents=related_documents,
        history=history,
        llm_provider=llm_result.provider,
        llm_model=llm_result.model,
        used_fallback=llm_result.used_fallback,
    )
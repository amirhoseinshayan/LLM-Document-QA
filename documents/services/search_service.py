import re
from dataclasses import dataclass

from documents.models import DocumentChunk


@dataclass
class SearchResult:
    """
    Store a chunk search result with its score.
    """
    chunk: DocumentChunk
    score: float


def normalize_text(text: str) -> str:
    """
    Normalize text for simple keyword-based search.
    """
    if not text:
        return ""

    text = text.lower()
    text = re.sub(r"[^\w\s\u0600-\u06FF]", " ", text)
    text = re.sub(r"\s+", " ", text)

    return text.strip()


def tokenize_query(query: str) -> list[str]:
    """
    Convert query text into searchable terms.
    """
    normalized_query = normalize_text(query)

    if not normalized_query:
        return []

    return [
        token
        for token in normalized_query.split(" ")
        if len(token) > 1
    ]


def calculate_chunk_score(chunk: DocumentChunk, query: str, query_terms: list[str]) -> float:
    """
    Calculate a simple relevance score for a chunk.
    """
    normalized_query = normalize_text(query)
    normalized_content = normalize_text(chunk.content)
    normalized_title = normalize_text(chunk.document.title)

    score = 0.0

    if not normalized_content:
        return score

    # Give a strong score when the full query appears in the chunk.
    if normalized_query and normalized_query in normalized_content:
        score += 5.0

    # Give a smaller score for each matched query term.
    for term in query_terms:
        if term in normalized_content:
            score += 1.0

        if term in normalized_title:
            score += 0.5

    # Prefer earlier chunks slightly because they often contain introductions.
    if chunk.chunk_index == 0:
        score += 0.2

    return score


def search_relevant_chunks(
    query: str,
    top_k: int = 5,
    document_id: int | None = None,
) -> list[SearchResult]:
    """
    Search document chunks and return the most relevant results.
    """
    query_terms = tokenize_query(query)

    if not query_terms:
        return []

    queryset = DocumentChunk.objects.select_related("document").all()

    if document_id:
        queryset = queryset.filter(document_id=document_id)

    results = []

    for chunk in queryset:
        score = calculate_chunk_score(chunk, query, query_terms)

        if score > 0:
            results.append(
                SearchResult(
                    chunk=chunk,
                    score=score,
                )
            )

    results.sort(key=lambda result: result.score, reverse=True)

    return results[:top_k]
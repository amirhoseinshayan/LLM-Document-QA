def split_text(text: str, chunk_size: int = 1000, chunk_overlap: int = 150) -> list[str]:
    """
    Split extracted text into overlapping chunks without external dependencies.
    """
    if not text:
        return []

    cleaned_text = text.strip()

    if len(cleaned_text) <= chunk_size:
        return [cleaned_text]

    chunks = []
    start = 0
    text_length = len(cleaned_text)

    while start < text_length:
        end = start + chunk_size
        chunk = cleaned_text[start:end].strip()

        if chunk:
            chunks.append(chunk)

        if end >= text_length:
            break

        # Keep overlap between chunks to preserve context.
        start = end - chunk_overlap

    return chunks
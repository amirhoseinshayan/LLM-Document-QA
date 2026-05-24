from langchain_text_splitters import RecursiveCharacterTextSplitter


def split_text(text: str) -> list[str]:
    """
    Split extracted document text into searchable chunks.
    """
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=150,
        separators=[
            "\n\n",
            "\n",
            ".",
            "!",
            "?",
            "؟",
            "؛",
            "،",
            " ",
            "",
        ],
    )

    chunks = splitter.split_text(text)

    # Remove empty chunks after splitting.
    return [
        chunk.strip()
        for chunk in chunks
        if chunk.strip()
    ]
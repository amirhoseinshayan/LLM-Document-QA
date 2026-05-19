from docx import Document as DocxDocument


def extract_text_from_docx(file_path: str) -> str:
    """
    Extract text from a .docx file.
    """
    doc = DocxDocument(file_path)

    paragraphs = []

    for paragraph in doc.paragraphs:
        text = paragraph.text.strip()
        if text:
            paragraphs.append(text)

    return "\n".join(paragraphs)
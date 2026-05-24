from pathlib import Path

from docx import Document as DocxDocument
from pypdf import PdfReader


SUPPORTED_FILE_EXTENSIONS = {".docx", ".pdf", ".txt"}


class UnsupportedFileTypeError(Exception):
    """
    Raised when the uploaded file type is not supported.
    """


class TextExtractionError(Exception):
    """
    Raised when text extraction fails.
    """


def get_file_extension(file_path: str) -> str:
    """
    Return the lowercase file extension.
    """
    return Path(file_path).suffix.lower()


def validate_supported_file(file_path: str) -> None:
    """
    Validate whether the uploaded file type is supported.
    """
    extension = get_file_extension(file_path)

    if extension not in SUPPORTED_FILE_EXTENSIONS:
        supported = ", ".join(sorted(SUPPORTED_FILE_EXTENSIONS))
        raise UnsupportedFileTypeError(
            f"Unsupported file type '{extension}'. Supported file types are: {supported}."
        )


def extract_text_from_docx(file_path: str) -> str:
    """
    Extract text from a DOCX file.
    """
    document = DocxDocument(file_path)

    paragraphs = [
        paragraph.text.strip()
        for paragraph in document.paragraphs
        if paragraph.text.strip()
    ]

    return "\n".join(paragraphs)


def extract_text_from_pdf(file_path: str) -> str:
    """
    Extract text from a PDF file.
    """
    reader = PdfReader(file_path)
    pages_text = []

    for page in reader.pages:
        text = page.extract_text() or ""

        if text.strip():
            pages_text.append(text.strip())

    return "\n\n".join(pages_text)


def extract_text_from_txt(file_path: str) -> str:
    """
    Extract text from a TXT file using common encodings.
    """
    encodings = ["utf-8", "utf-8-sig", "cp1256", "latin-1"]

    for encoding in encodings:
        try:
            with open(file_path, "r", encoding=encoding) as file:
                return file.read().strip()
        except UnicodeDecodeError:
            continue

    raise TextExtractionError("Could not decode TXT file with supported encodings.")


def extract_text_from_file(file_path: str) -> str:
    """
    Extract text from a supported document file.
    """
    validate_supported_file(file_path)

    extension = get_file_extension(file_path)

    try:
        if extension == ".docx":
            text = extract_text_from_docx(file_path)
        elif extension == ".pdf":
            text = extract_text_from_pdf(file_path)
        elif extension == ".txt":
            text = extract_text_from_txt(file_path)
        else:
            raise UnsupportedFileTypeError(f"Unsupported file type: {extension}")
    except UnsupportedFileTypeError:
        raise
    except Exception as exc:
        raise TextExtractionError(f"Text extraction failed: {exc}") from exc

    if not text.strip():
        raise TextExtractionError("No readable text could be extracted from the file.")

    return text.strip()
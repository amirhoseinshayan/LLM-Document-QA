from documents.models import DocumentChunk
from documents.services.chunker import chunk_text
from documents.services.docx_extractor import extract_text_from_docx


def process_document(document):
    """
    Extract text from a document file and create text chunks.
    """
    try:
        full_text = extract_text_from_docx(document.file.path)

        document.full_text = full_text
        document.is_processed = True
        document.processing_error = ""

        document.save(
            update_fields=[
                "full_text",
                "is_processed",
                "processing_error",
                "updated_at",
            ]
        )

        document.chunks.all().delete()

        chunks = chunk_text(full_text)

        chunk_objects = [
            DocumentChunk(
                document=document,
                content=chunk,
                chunk_index=index,
            )
            for index, chunk in enumerate(chunks)
        ]

        DocumentChunk.objects.bulk_create(chunk_objects)

        return True

    except Exception as exc:
        document.is_processed = False
        document.processing_error = str(exc)
        document.save(
            update_fields=[
                "is_processed",
                "processing_error",
                "updated_at",
            ]
        )
        return False
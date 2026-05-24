from django.db import transaction

from documents.models import DocumentChunk
from documents.services.file_extractor import extract_text_from_file
from documents.services.text_splitter import split_text


def process_document(document):
    """
    Extract text from a document, create chunks, and update processing status.
    """
    try:
        if not document.file:
            raise ValueError("No file was uploaded for this document.")

        full_text = extract_text_from_file(document.file.path)
        chunks = split_text(full_text)

        with transaction.atomic():
            # Remove old chunks before creating new ones.
            DocumentChunk.objects.filter(document=document).delete()

            document.full_text = full_text
            document.is_processed = True
            document.processing_error = ""
            document.save()

            for index, chunk in enumerate(chunks):
                DocumentChunk.objects.create(
                    document=document,
                    content=chunk,
                    chunk_index=index,
                )

        return True

    except Exception as exc:
        document.full_text = ""
        document.is_processed = False
        document.processing_error = str(exc)
        document.save()

        return False
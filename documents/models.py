from django.core.exceptions import ValidationError
from django.db import models
from django.core.validators import FileExtensionValidator
from pathlib import Path


def validate_docx_file(file):
    if not file.name.lower().endswith(".docx"):
        raise ValidationError("Only .docx files are allowed.")


class Document(models.Model):
    """
    Uploaded document model.
    """

    title = models.CharField(max_length=255)

    file = models.FileField(
        upload_to="documents/",
        validators=[
            FileExtensionValidator(
                allowed_extensions=["docx", "pdf", "txt"],
                message="Only DOCX, PDF, and TXT files are supported.",
            )
        ],
    )
    full_text = models.TextField(blank=True)
    is_processed = models.BooleanField(default=False)
    processing_error = models.TextField(blank=True)

    uploaded_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


    class Meta:
        ordering = ["-uploaded_at"]

    @property
    def file_extension(self):
        """
        Return the uploaded file extension without the dot.
        """
        if not self.file:
            return ""

        return Path(self.file.name).suffix.lower().replace(".", "")

    @property
    def file_type_label(self):
        """
        Return a readable file type label for the UI.
        """
        extension = self.file_extension

        if not extension:
            return "Document"

        return extension.upper()

    def __str__(self):
        return self.title


class DocumentChunk(models.Model):
    document = models.ForeignKey(
        Document,
        on_delete=models.CASCADE,
        related_name="chunks",
    )
    content = models.TextField()
    chunk_index = models.PositiveIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["document", "chunk_index"]
        unique_together = ["document", "chunk_index"]

    def __str__(self):
        return f"{self.document.title} - Chunk {self.chunk_index}"


class QuestionAnswer(models.Model):
    question = models.TextField()
    answer = models.TextField()
    related_documents = models.ManyToManyField(
        Document,
        blank=True,
        related_name="question_answers",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.question[:80]
from django.contrib import admin

from documents.models import Document, DocumentChunk, QuestionAnswer
from documents.services.document_processor import process_document


class DocumentChunkInline(admin.TabularInline):
    model = DocumentChunk
    extra = 0
    readonly_fields = ["chunk_index", "content", "created_at"]
    can_delete = False
    max_num = 0


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = [
        "title",
        "is_processed",
        "chunk_count",
        "uploaded_at",
        "updated_at",
    ]
    list_filter = ["is_processed", "uploaded_at"]
    search_fields = ["title", "full_text"]
    readonly_fields = [
        "full_text",
        "is_processed",
        "processing_error",
        "uploaded_at",
        "updated_at",
    ]
    inlines = [DocumentChunkInline]
    actions = ["reprocess_documents"]

    fieldsets = (
        (
            "Document Info",
            {
                "fields": (
                    "title",
                    "file",
                )
            },
        ),
        (
            "Processed Text",
            {
                "fields": (
                    "full_text",
                    "is_processed",
                    "processing_error",
                )
            },
        ),
        (
            "Timestamps",
            {
                "fields": (
                    "uploaded_at",
                    "updated_at",
                )
            },
        ),
    )

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        process_document(obj)

    def chunk_count(self, obj):
        return obj.chunks.count()

    chunk_count.short_description = "Chunks"

    @admin.action(description="Reprocess selected documents")
    def reprocess_documents(self, request, queryset):
        success_count = 0

        for document in queryset:
            if process_document(document):
                success_count += 1

        self.message_user(
            request,
            f"{success_count} document(s) reprocessed successfully.",
        )


@admin.register(DocumentChunk)
class DocumentChunkAdmin(admin.ModelAdmin):
    list_display = ["document", "chunk_index", "short_content", "created_at"]
    list_filter = ["created_at"]
    search_fields = ["content", "document__title"]
    readonly_fields = ["document", "chunk_index", "content", "created_at"]

    def short_content(self, obj):
        return obj.content[:120] + "..." if len(obj.content) > 120 else obj.content

    short_content.short_description = "Content"


@admin.register(QuestionAnswer)
class QuestionAnswerAdmin(admin.ModelAdmin):
    list_display = ["short_question", "short_answer", "created_at"]
    search_fields = ["question", "answer"]
    list_filter = ["created_at"]
    readonly_fields = ["created_at"]

    def short_question(self, obj):
        return obj.question[:100] + "..." if len(obj.question) > 100 else obj.question

    def short_answer(self, obj):
        return obj.answer[:100] + "..." if len(obj.answer) > 100 else obj.answer

    short_question.short_description = "Question"
    short_answer.short_description = "Answer"
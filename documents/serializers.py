from rest_framework import serializers

from documents.models import Document, DocumentChunk, QuestionAnswer


class DocumentChunkSerializer(serializers.ModelSerializer):
    document_title = serializers.CharField(source="document.title", read_only=True)

    class Meta:
        model = DocumentChunk
        fields = [
            "id",
            "document",
            "document_title",
            "content",
            "chunk_index",
            "created_at",
        ]
        read_only_fields = [
            "id",
            "document_title",
            "created_at",
        ]


class DocumentSerializer(serializers.ModelSerializer):
    chunk_count = serializers.SerializerMethodField()

    class Meta:
        model = Document
        fields = [
            "id",
            "title",
            "file",
            "full_text",
            "is_processed",
            "processing_error",
            "chunk_count",
            "uploaded_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "full_text",
            "is_processed",
            "processing_error",
            "chunk_count",
            "uploaded_at",
            "updated_at",
        ]

    def get_chunk_count(self, obj):
        return obj.chunks.count()


class DocumentDetailSerializer(serializers.ModelSerializer):
    chunks = DocumentChunkSerializer(many=True, read_only=True)
    chunk_count = serializers.SerializerMethodField()

    class Meta:
        model = Document
        fields = [
            "id",
            "title",
            "file",
            "full_text",
            "is_processed",
            "processing_error",
            "chunk_count",
            "chunks",
            "uploaded_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "full_text",
            "is_processed",
            "processing_error",
            "chunk_count",
            "chunks",
            "uploaded_at",
            "updated_at",
        ]

    def get_chunk_count(self, obj):
        return obj.chunks.count()


class QuestionAnswerSerializer(serializers.ModelSerializer):
    related_documents_titles = serializers.SerializerMethodField()

    class Meta:
        model = QuestionAnswer
        fields = [
            "id",
            "question",
            "answer",
            "related_documents",
            "related_documents_titles",
            "created_at",
        ]
        read_only_fields = [
            "id",
            "related_documents_titles",
            "created_at",
        ]

    def get_related_documents_titles(self, obj):
        return [document.title for document in obj.related_documents.all()]
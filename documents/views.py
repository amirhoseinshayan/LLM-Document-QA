from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.response import Response

from documents.models import Document, DocumentChunk, QuestionAnswer
from documents.serializers import (
    DocumentChunkSerializer,
    DocumentDetailSerializer,
    DocumentSerializer,
    QuestionAnswerSerializer,
)
from documents.services.document_processor import process_document


class DocumentViewSet(viewsets.ModelViewSet):
    queryset = Document.objects.all()
    parser_classes = [MultiPartParser, FormParser]

    def get_serializer_class(self):
        if self.action == "retrieve":
            return DocumentDetailSerializer
        return DocumentSerializer

    def perform_create(self, serializer):
        document = serializer.save()
        process_document(document)

    def perform_update(self, serializer):
        document = serializer.save()

        if "file" in self.request.FILES:
            process_document(document)

    @action(detail=True, methods=["post"])
    def reprocess(self, request, pk=None):
        document = self.get_object()
        success = process_document(document)

        if success:
            serializer = self.get_serializer(document)
            return Response(
                {
                    "message": "Document reprocessed successfully.",
                    "document": serializer.data,
                },
                status=status.HTTP_200_OK,
            )

        return Response(
            {
                "message": "Document reprocessing failed.",
                "error": document.processing_error,
            },
            status=status.HTTP_400_BAD_REQUEST,
        )


class DocumentChunkViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = DocumentChunk.objects.select_related("document").all()
    serializer_class = DocumentChunkSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        document_id = self.request.query_params.get("document")

        if document_id:
            queryset = queryset.filter(document_id=document_id)

        return queryset


class QuestionAnswerViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = QuestionAnswer.objects.prefetch_related("related_documents").all()
    serializer_class = QuestionAnswerSerializer
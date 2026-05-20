from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.response import Response
from rest_framework.views import APIView

from documents.models import Document, DocumentChunk, QuestionAnswer
from documents.serializers import (
    DocumentChunkSerializer,
    DocumentDetailSerializer,
    DocumentSearchRequestSerializer,
    DocumentSerializer,
    QuestionAnswerSerializer,
)
from documents.services.document_processor import process_document
from documents.services.search_service import search_relevant_chunks


class DocumentViewSet(viewsets.ModelViewSet):
    queryset = Document.objects.all()
    parser_classes = [MultiPartParser, FormParser]

    def get_serializer_class(self):
        if self.action == "retrieve":
            return DocumentDetailSerializer
        return DocumentSerializer

    def perform_create(self, serializer):
        # Process the uploaded document after saving it.
        document = serializer.save()
        process_document(document)

    def perform_update(self, serializer):
        # Reprocess the document only when a new file is uploaded.
        document = serializer.save()

        if "file" in self.request.FILES:
            process_document(document)

    @action(detail=True, methods=["post"])
    def reprocess(self, request, pk=None):
        # Manually reprocess a document and recreate its chunks.
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
        # Optionally filter chunks by document ID.
        queryset = super().get_queryset()
        document_id = self.request.query_params.get("document")

        if document_id:
            queryset = queryset.filter(document_id=document_id)

        return queryset


class QuestionAnswerViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = QuestionAnswer.objects.prefetch_related("related_documents").all()
    serializer_class = QuestionAnswerSerializer


class DocumentSearchAPIView(APIView):
    """
    Search relevant document chunks for a given query.
    """

    def post(self, request):
        request_serializer = DocumentSearchRequestSerializer(data=request.data)
        request_serializer.is_valid(raise_exception=True)

        query = request_serializer.validated_data["query"]
        top_k = request_serializer.validated_data.get("top_k", 5)
        document_id = request_serializer.validated_data.get("document_id")

        results = search_relevant_chunks(
            query=query,
            top_k=top_k,
            document_id=document_id,
        )

        # Serialize each chunk only once to avoid nested relation errors.
        response_results = [
            {
                "score": result.score,
                "chunk": DocumentChunkSerializer(
                    result.chunk,
                    context={"request": request},
                ).data,
            }
            for result in results
        ]

        return Response(
            {
                "query": query,
                "count": len(response_results),
                "results": response_results,
            },
            status=status.HTTP_200_OK,
        )
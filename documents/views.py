from drf_spectacular.utils import (
    OpenApiExample,
    OpenApiParameter,
    extend_schema,
    extend_schema_view,
)
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.response import Response
from rest_framework.views import APIView

from documents.models import Document, DocumentChunk, QuestionAnswer
from documents.serializers import (
    AskQuestionRequestSerializer,
    AskQuestionResponseSerializer,
    DocumentChunkSerializer,
    DocumentDetailSerializer,
    DocumentSearchRequestSerializer,
    DocumentSerializer,
    QuestionAnswerSerializer,
)
from documents.services.document_processor import process_document
from documents.services.llm_service import LLMConfigurationError
from documents.services.rag_service import answer_question_with_rag
from documents.services.search_service import search_relevant_chunks


@extend_schema_view(
    list=extend_schema(
        summary="List documents",
        description="Return all uploaded documents with processing status and chunk count.",
        tags=["Documents"],
    ),
    create=extend_schema(
        summary="Upload a document",
        description=(
            "Upload a DOCX document. The system automatically extracts full text "
            "and creates document chunks after saving the file."
        ),
        tags=["Documents"],
    ),
    retrieve=extend_schema(
        summary="Retrieve document details",
        description="Return a single document with its extracted text and generated chunks.",
        tags=["Documents"],
    ),
    update=extend_schema(
        summary="Update a document",
        description=(
            "Fully update a document. If a new file is uploaded, the document "
            "is reprocessed and chunks are recreated."
        ),
        tags=["Documents"],
    ),
    partial_update=extend_schema(
        summary="Partially update a document",
        description=(
            "Partially update a document. If a new file is uploaded, the document "
            "is reprocessed and chunks are recreated."
        ),
        tags=["Documents"],
    ),
    destroy=extend_schema(
        summary="Delete a document",
        description="Delete a document and all related chunks.",
        tags=["Documents"],
    ),
)
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

    @extend_schema(
        summary="Reprocess a document",
        description=(
            "Manually reprocess an existing document. This extracts text again, "
            "deletes old chunks, and creates new chunks."
        ),
        tags=["Documents"],
        responses={200: DocumentSerializer},
    )
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


@extend_schema_view(
    list=extend_schema(
        summary="List document chunks",
        description="Return all generated document chunks. Can be filtered by document ID.",
        tags=["Chunks"],
        parameters=[
            OpenApiParameter(
                name="document",
                description="Filter chunks by document ID.",
                required=False,
                type=int,
            )
        ],
    ),
    retrieve=extend_schema(
        summary="Retrieve a document chunk",
        description="Return a single document chunk by ID.",
        tags=["Chunks"],
    ),
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


@extend_schema_view(
    list=extend_schema(
        summary="List question-answer history",
        description="Return all saved question-answer records.",
        tags=["History"],
    ),
    retrieve=extend_schema(
        summary="Retrieve a question-answer record",
        description="Return a single saved question-answer record by ID.",
        tags=["History"],
    ),
)
class QuestionAnswerViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = QuestionAnswer.objects.prefetch_related("related_documents").all()
    serializer_class = QuestionAnswerSerializer


class DocumentSearchAPIView(APIView):
    """
    Search relevant document chunks for a given query.
    """

    @extend_schema(
        summary="Search relevant chunks",
        description=(
            "Search uploaded document chunks and return the most relevant chunks "
            "for a given query. This endpoint is used before answer generation."
        ),
        tags=["Search"],
        request=DocumentSearchRequestSerializer,
        responses={
            200: {
                "type": "object",
                "properties": {
                    "query": {"type": "string"},
                    "count": {"type": "integer"},
                    "results": {
                        "type": "array",
                        "items": {"type": "object"},
                    },
                },
            }
        },
        examples=[
            OpenApiExample(
                "Search request",
                value={
                    "query": "ادبیات",
                    "top_k": 5,
                },
                request_only=True,
            ),
            OpenApiExample(
                "Search request with document filter",
                value={
                    "query": "Django",
                    "top_k": 5,
                    "document_id": 1,
                },
                request_only=True,
            ),
        ],
    )
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


class AskQuestionAPIView(APIView):
    """
    Answer a user question based on uploaded documents.
    """

    @extend_schema(
        summary="Ask a question",
        description=(
            "Receive a user question, retrieve relevant document chunks, build context, "
            "generate an answer using the configured LLM provider, and save the result "
            "in question-answer history."
        ),
        tags=["Ask"],
        request=AskQuestionRequestSerializer,
        responses={200: AskQuestionResponseSerializer},
        examples=[
            OpenApiExample(
                "Ask request",
                value={
                    "question": "در این سند درباره ادبیات چه گفته شده است؟",
                    "top_k": 5,
                },
                request_only=True,
            ),
            OpenApiExample(
                "Ask request with document filter",
                value={
                    "question": "What does the document say about Django?",
                    "top_k": 5,
                    "document_id": 1,
                },
                request_only=True,
            ),
        ],
    )
    def post(self, request):
        request_serializer = AskQuestionRequestSerializer(data=request.data)
        request_serializer.is_valid(raise_exception=True)

        question = request_serializer.validated_data["question"]
        top_k = request_serializer.validated_data.get("top_k", 5)
        document_id = request_serializer.validated_data.get("document_id")

        try:
            result = answer_question_with_rag(
                question=question,
                top_k=top_k,
                document_id=document_id,
            )
        except LLMConfigurationError as exc:
            return Response(
                {
                    "message": "LLM configuration error.",
                    "error": str(exc),
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
        except Exception as exc:
            return Response(
                {
                    "message": "Answer generation failed.",
                    "error": str(exc),
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        response_data = {
            "question": result.question,
            "answer": result.answer,
            "used_chunks_count": len(result.used_chunks),
            "related_documents": [
                {
                    "id": document.id,
                    "title": document.title,
                }
                for document in result.related_documents
            ],
            "history_id": result.history.id,
        }

        response_serializer = AskQuestionResponseSerializer(response_data)

        return Response(
            response_serializer.data,
            status=status.HTTP_200_OK,
        )
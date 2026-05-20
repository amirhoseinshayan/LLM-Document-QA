from django.urls import include, path
from rest_framework.routers import DefaultRouter

from documents.views import (
    AskQuestionAPIView,
    DocumentChunkViewSet,
    DocumentSearchAPIView,
    DocumentViewSet,
    QuestionAnswerViewSet,
)

router = DefaultRouter()
router.register("documents", DocumentViewSet, basename="document")
router.register("chunks", DocumentChunkViewSet, basename="chunk")
router.register("history", QuestionAnswerViewSet, basename="history")

urlpatterns = [
    path("ask/", AskQuestionAPIView.as_view(), name="ask-question"),
    path("search/", DocumentSearchAPIView.as_view(), name="document-search"),
    path("", include(router.urls)),
]
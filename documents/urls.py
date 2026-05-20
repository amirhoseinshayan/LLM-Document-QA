from django.urls import include, path
from rest_framework.routers import DefaultRouter

from documents.views import (
    DocumentChunkViewSet,
    DocumentViewSet,
    QuestionAnswerViewSet,
)

router = DefaultRouter()
router.register("documents", DocumentViewSet, basename="document")
router.register("chunks", DocumentChunkViewSet, basename="chunk")
router.register("history", QuestionAnswerViewSet, basename="history")

urlpatterns = [
    path("", include(router.urls)),
]
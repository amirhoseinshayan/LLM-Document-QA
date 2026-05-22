from django.urls import path

from documents import ui_views

urlpatterns = [
    path("", ui_views.home_view, name="ui-home"),
    path("documents/", ui_views.document_list_view, name="ui-document-list"),
    path("documents/upload/", ui_views.document_upload_view, name="ui-document-upload"),
    path("documents/<int:pk>/", ui_views.document_detail_view, name="ui-document-detail"),
    path("documents/<int:pk>/edit/", ui_views.document_update_view, name="ui-document-update"),
    path("documents/<int:pk>/delete/", ui_views.document_delete_view, name="ui-document-delete"),
    path(
        "documents/<int:pk>/reprocess/",
        ui_views.document_reprocess_view,
        name="ui-document-reprocess",
    ),
    path("search/", ui_views.search_view, name="ui-search"),
    path("ask/", ui_views.ask_view, name="ui-ask"),
    path("history/", ui_views.history_view, name="ui-history"),
    path("history/clear/", ui_views.history_clear_view, name="ui-history-clear"),
    path("history/<int:pk>/", ui_views.history_detail_view, name="ui-history-detail"),
    path("history/<int:pk>/delete/", ui_views.history_delete_view, name="ui-history-delete"),
]
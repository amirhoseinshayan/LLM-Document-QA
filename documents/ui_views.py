from django.conf import settings
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from documents.services.llm_service import get_llm_status
from documents.forms import (
    AskQuestionForm,
    DocumentFilterForm,
    DocumentUpdateForm,
    DocumentUploadForm,
    SearchForm,
)
from documents.models import Document, QuestionAnswer
from documents.services.document_processor import process_document
from documents.services.rag_service import answer_question_with_rag
from documents.services.search_service import search_relevant_chunks


def home_view(request):
    """
    Render the main dashboard page.
    """
    documents_count = Document.objects.count()
    processed_documents_count = Document.objects.filter(is_processed=True).count()
    history_count = QuestionAnswer.objects.count()
    latest_documents = Document.objects.all()[:15]
    latest_history_items = QuestionAnswer.objects.all()[:15]
    llm_status = get_llm_status()

    context = {
        "documents_count": documents_count,
        "processed_documents_count": processed_documents_count,
        "history_count": history_count,
        "latest_documents": latest_documents,
        "latest_history_items": latest_history_items,
        "llm_provider": settings.LLM_PROVIDER,
        "llm_status": llm_status,
    }

    return render(request, "documents/home.html", context)


def document_list_view(request):
    """
    Render a searchable and filterable list of uploaded documents.
    """
    form = DocumentFilterForm(request.GET or None)
    documents = Document.objects.all()

    if form.is_valid():
        query = form.cleaned_data.get("query")
        status = form.cleaned_data.get("status")

        if query:
            documents = documents.filter(title__icontains=query)

        if status == "processed":
            documents = documents.filter(is_processed=True)
        elif status == "not_processed":
            documents = documents.filter(is_processed=False)

    return render(
        request,
        "documents/document_list.html",
        {
            "documents": documents,
            "form": form,
        },
    )


def document_detail_view(request, pk):
    """
    Render details of a single document and its chunks.
    """
    document = get_object_or_404(Document, pk=pk)
    chunks = document.chunks.all()

    return render(
        request,
        "documents/document_detail.html",
        {
            "document": document,
            "chunks": chunks,
        },
    )


def document_upload_view(request):
    """
    Upload a DOCX document and process it.
    """
    if request.method == "POST":
        form = DocumentUploadForm(request.POST, request.FILES)

        if form.is_valid():
            document = form.save()
            process_document(document)

            if document.is_processed:
                messages.success(request, "Document uploaded and processed successfully.")
            else:
                messages.error(request, "Document uploaded, but processing failed.")

            return redirect("ui-document-detail", pk=document.pk)
    else:
        form = DocumentUploadForm()

    return render(
        request,
        "documents/document_upload.html",
        {
            "form": form,
        },
    )


def document_update_view(request, pk):
    """
    Update document title or replace the uploaded file.
    """
    document = get_object_or_404(Document, pk=pk)

    if request.method == "POST":
        form = DocumentUpdateForm(
            request.POST,
            request.FILES,
            instance=document,
        )

        if form.is_valid():
            has_new_file = "file" in request.FILES
            document = form.save()

            if has_new_file:
                process_document(document)
                messages.success(request, "Document updated and reprocessed successfully.")
            else:
                messages.success(request, "Document updated successfully.")

            return redirect("ui-document-detail", pk=document.pk)
    else:
        form = DocumentUpdateForm(instance=document)

    return render(
        request,
        "documents/document_update.html",
        {
            "form": form,
            "document": document,
        },
    )


def document_delete_view(request, pk):
    """
    Delete a document from the user interface.
    """
    document = get_object_or_404(Document, pk=pk)

    if request.method == "POST":
        document.delete()
        messages.success(request, "Document deleted successfully.")
        return redirect("ui-document-list")

    return render(
        request,
        "documents/document_confirm_delete.html",
        {
            "document": document,
        },
    )


def document_reprocess_view(request, pk):
    """
    Reprocess an existing document from the user interface.
    """
    document = get_object_or_404(Document, pk=pk)

    if request.method == "POST":
        success = process_document(document)

        if success:
            messages.success(request, "Document reprocessed successfully.")
        else:
            messages.error(request, "Document reprocessing failed.")

    return redirect("ui-document-detail", pk=document.pk)


def search_view(request):
    """
    Search relevant chunks using the user interface.
    """
    results = []
    query = None
    selected_document = None

    if request.method == "POST":
        form = SearchForm(request.POST)

        if form.is_valid():
            query = form.cleaned_data["query"]
            top_k = form.cleaned_data.get("top_k") or 5
            selected_document = form.cleaned_data.get("document")
            document_id = selected_document.id if selected_document else None

            results = search_relevant_chunks(
                query=query,
                top_k=top_k,
                document_id=document_id,
            )
    else:
        form = SearchForm()

    return render(
        request,
        "documents/search.html",
        {
            "form": form,
            "query": query,
            "selected_document": selected_document,
            "results": results,
        },
    )


def ask_view(request):
    """
    Ask a question and generate an answer from retrieved document chunks.
    """
    rag_result = None
    selected_document = None

    if request.method == "POST":
        form = AskQuestionForm(request.POST)

        if form.is_valid():
            question = form.cleaned_data["question"]
            top_k = form.cleaned_data.get("top_k") or 5
            selected_document = form.cleaned_data.get("document")
            document_id = selected_document.id if selected_document else None

            rag_result = answer_question_with_rag(
                question=question,
                top_k=top_k,
                document_id=document_id,
            )

            messages.success(request, "Question answered and saved to history.")
    else:
        form = AskQuestionForm()

    return render(
        request,
        "documents/ask.html",
        {
            "form": form,
            "rag_result": rag_result,
            "selected_document": selected_document,
        },
    )


def history_view(request):
    """
    Render saved question-answer history.
    """
    history_items = QuestionAnswer.objects.prefetch_related("related_documents").all()

    return render(
        request,
        "documents/history.html",
        {
            "history_items": history_items,
        },
    )


def history_detail_view(request, pk):
    """
    Render details of a single question-answer history item.
    """
    history_item = get_object_or_404(
        QuestionAnswer.objects.prefetch_related("related_documents"),
        pk=pk,
    )

    return render(
        request,
        "documents/history_detail.html",
        {
            "history_item": history_item,
        },
    )


def history_delete_view(request, pk):
    """
    Delete a single question-answer history item.
    """
    history_item = get_object_or_404(QuestionAnswer, pk=pk)

    if request.method == "POST":
        history_item.delete()
        messages.success(request, "History item deleted successfully.")
        return redirect("ui-history")

    return render(
        request,
        "documents/history_confirm_delete.html",
        {
            "history_item": history_item,
        },
    )


def history_clear_view(request):
    """
    Delete all question-answer history items.
    """
    if request.method == "POST":
        QuestionAnswer.objects.all().delete()
        messages.success(request, "All history items deleted successfully.")
        return redirect("ui-history")

    return render(request, "documents/history_confirm_clear.html")
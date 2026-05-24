from django import forms

from documents.models import Document
from documents.services.file_extractor import SUPPORTED_FILE_EXTENSIONS


def validate_uploaded_file_extension(uploaded_file):
    """
    Validate uploaded file extension in UI forms.
    """
    if not uploaded_file:
        return

    file_name = uploaded_file.name.lower()
    is_supported = any(
        file_name.endswith(extension)
        for extension in SUPPORTED_FILE_EXTENSIONS
    )

    if not is_supported:
        supported = ", ".join(sorted(SUPPORTED_FILE_EXTENSIONS))
        raise forms.ValidationError(
            f"Unsupported file type. Supported file types are: {supported}."
        )


class DocumentUploadForm(forms.ModelForm):
    """
    Form for uploading supported document files from the user interface.
    """

    class Meta:
        model = Document
        fields = ["title", "file"]
        widgets = {
            "title": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter document title",
                }
            ),
            "file": forms.FileInput(
                attrs={
                    "class": "form-control",
                    "accept": ".docx,.pdf,.txt",
                }
            ),
        }

    def clean_file(self):
        uploaded_file = self.cleaned_data.get("file")
        validate_uploaded_file_extension(uploaded_file)
        return uploaded_file


class DocumentUpdateForm(forms.ModelForm):
    """
    Form for updating document title or replacing the uploaded file.
    """

    class Meta:
        model = Document
        fields = ["title", "file"]
        widgets = {
            "title": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter document title",
                }
            ),
            "file": forms.FileInput(
                attrs={
                    "class": "form-control",
                    "accept": ".docx,.pdf,.txt",
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Keep the current file if the user does not upload a new one.
        self.fields["file"].required = False

    def clean_file(self):
        uploaded_file = self.cleaned_data.get("file")
        validate_uploaded_file_extension(uploaded_file)
        return uploaded_file


class DocumentFilterForm(forms.Form):
    """
    Form for filtering documents in the user interface.
    """

    STATUS_CHOICES = [
        ("", "All statuses"),
        ("processed", "Processed"),
        ("not_processed", "Not processed"),
    ]

    query = forms.CharField(
        max_length=255,
        required=False,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "Search by document title",
            }
        ),
    )
    status = forms.ChoiceField(
        choices=STATUS_CHOICES,
        required=False,
        widget=forms.Select(
            attrs={
                "class": "form-control",
            }
        ),
    )


class SearchForm(forms.Form):
    """
    Form for searching relevant document chunks.
    """

    query = forms.CharField(
        max_length=1000,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "Enter your search query",
            }
        ),
    )
    top_k = forms.IntegerField(
        min_value=1,
        max_value=20,
        initial=5,
        required=False,
        widget=forms.NumberInput(
            attrs={
                "class": "form-control",
            }
        ),
    )
    document = forms.ModelChoiceField(
        queryset=Document.objects.all(),
        required=False,
        empty_label="All documents",
        widget=forms.Select(
            attrs={
                "class": "form-control",
            }
        ),
    )


class AskQuestionForm(forms.Form):
    """
    Form for asking questions about uploaded documents.
    """

    question = forms.CharField(
        max_length=2000,
        widget=forms.Textarea(
            attrs={
                "class": "form-control",
                "placeholder": "Ask a question about your documents",
                "rows": 4,
            }
        ),
    )
    top_k = forms.IntegerField(
        min_value=1,
        max_value=20,
        initial=5,
        required=False,
        widget=forms.NumberInput(
            attrs={
                "class": "form-control",
            }
        ),
    )
    document = forms.ModelChoiceField(
        queryset=Document.objects.all(),
        required=False,
        empty_label="All documents",
        widget=forms.Select(
            attrs={
                "class": "form-control",
            }
        ),
    )
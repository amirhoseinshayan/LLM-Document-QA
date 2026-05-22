from django import forms

from documents.models import Document


class DocumentUploadForm(forms.ModelForm):
    """
    Form for uploading DOCX documents from the user interface.
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
                    "accept": ".docx",
                }
            ),
        }


class DocumentUpdateForm(forms.ModelForm):
    """
    Form for updating document title or replacing the DOCX file.
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
                    "accept": ".docx",
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Keep the current file if the user does not upload a new one.
        self.fields["file"].required = False


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
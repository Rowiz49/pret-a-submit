from django import forms
from django.forms import inlineformset_factory, BaseInlineFormSet
from .models import Conference, Question

class ConferenceForm(forms.ModelForm):
    class Meta:
        model = Conference
        fields = ["name"]
        widgets = {
            "name": forms.TextInput(
                attrs={"placeholder": "Conference name"}
            ),
        }

class BaseQuestionFormSet(BaseInlineFormSet):
    default_error_messages = {
        "too_few_forms": " Please submit at least 1 question.",
    }


QuestionFormSet = inlineformset_factory(
    Conference,
    Question,
    fields=["question_text", "position"],
    exclude=["id"], 
    widgets={
        "question_text": forms.Textarea(
            attrs={
                "class": "textarea textarea-sm w-full",
                "rows": 1,
                "placeholder": "Enter a question...",
                "required": False
            }
        )
    },
    extra=0,
    can_delete=True,
    min_num=1,
    validate_min=True,
    formset=BaseQuestionFormSet
)

class PaperUploadForm(forms.Form):
    """Form for uploading and processing academic papers"""
    INPUT_CLASS = 'input input-sm w-full'
    
    conference = forms.ModelChoiceField(
        queryset=Conference.objects.all(),
        required=True,
        empty_label="-- Choose a conference --",
        widget=forms.Select(attrs={
            'id': 'conference',
            'class': 'select select-sm w-full',
        })
    )
    
    ollama_url = forms.URLField(
        required=True,
        initial='http://localhost:11434',
        widget=forms.URLInput(attrs={
            'id': 'ollama_url',
            'class': INPUT_CLASS,
            'placeholder': 'http://localhost:11434',
        })
    )
    
    ollama_model = forms.CharField(
        required=True,
        widget=forms.TextInput(attrs={
            'id': 'ollama_model',
            'class': INPUT_CLASS,
            'placeholder': 'llama3, mistral, etc.',
        })
    )
    
    ollama_api_key = forms.CharField(
        required=False,
        widget=forms.PasswordInput(attrs={
            'id': 'ollama_api_key',
            'class': INPUT_CLASS,
            'placeholder': 'Optional API key',
        })
    )
    
    files = forms.FileField(
        required=True,
        widget=forms.FileInput(attrs={
            'id': 'file-input',
            'class': 'file-input file-input-bordered w-full pr-24',
            'accept': '.pdf',
        })
    )
    
    def clean_files(self):
        """Validate that the uploaded file is a PDF"""
        file = self.cleaned_data.get('files')
        if file and  not file.name.endswith('.pdf'):
                raise forms.ValidationError('Only PDF files are allowed.')
        return file
    
    def clean_ollama_url(self):
        """Validate Ollama URL format"""
        url = self.cleaned_data.get('ollama_url')
        if url and not (url.startswith('http://') or url.startswith('https://')):
            raise forms.ValidationError('Please enter a valid URL starting with http:// or https://')
        return url
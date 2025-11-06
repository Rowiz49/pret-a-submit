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
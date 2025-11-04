from django import forms
from django.forms import inlineformset_factory
from .models import Conference, Question


class ConferenceForm(forms.ModelForm):
    class Meta:
        model = Conference
        fields = ["name"]


QuestionFormSet = inlineformset_factory(
    Conference,
    Question,
    fields=["question_text"],
    extra=1,
    can_delete=True
)
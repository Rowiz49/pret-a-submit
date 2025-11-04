from django.shortcuts import render, redirect
from django.views import View
from .models import Conference
from .forms import ConferenceForm, QuestionFormSet


def index(request):
    conferences = Conference.objects.all()
    context = {"conferences": conferences}
    return render(request, "paper_grader/index.html", context)

class ConferenceCreateView(View):
    template_name = "paper_grader/conference_form.html"

    def get(self, request):
        return render(request, self.template_name, {
            "conference_form": ConferenceForm(),
            "formset": QuestionFormSet(),
        })

    def post(self, request):
        conference_form = ConferenceForm(request.POST)
        formset = QuestionFormSet(request.POST)

        if conference_form.is_valid() and formset.is_valid():
            conference = conference_form.save()
            formset.instance = conference
            formset.save()
            return redirect("index")

        return render(request, self.template_name, {
            "conference_form": conference_form,
            "formset": formset,
        })


# Generated migration for NeurIPS conference questions

from django.db import migrations


def add_conference_NeurIPS_questions(apps, schema_editor):
    Conference = apps.get_model('paper_grader', 'Conference')
    Question = apps.get_model('paper_grader', 'Question')

    conference, _ = Conference.objects.get_or_create(name='NeurIPS')

    questions = [
        "Do the main claims made in the abstract and introduction accurately reflect the paper's contributions and scope?",
        "Does the paper discuss the limitations of the work, including assumptions and how robust the results are to violations of those assumptions?",
        "If theoretical results are included, are the full set of assumptions stated and complete proofs of all theoretical results provided?",
        "If the contribution is a dataset or model, does the paper describe sufficient steps taken to make the results reproducible or verifiable?",
        "If experiments were run, does the paper include the code, data, and instructions needed to reproduce the main experimental results?",
        "If experiments were run, does the paper specify all training details (e.g., data splits, hyperparameters, how they were chosen)?",
        "Does the paper report error bars or other appropriate information about the statistical significance of the experiments?",
        "For each experiment, does the paper provide sufficient information on the compute resources (type of workers, memory, execution time) needed to reproduce the experiments?",
        "Have the authors read the NeurIPS Code of Ethics and ensured that their research conforms to it?",
        "If appropriate, does the paper discuss potential negative societal impacts of the work?",
        "Are safeguards in place for responsible release of models or datasets with a high risk for misuse?",
        "If existing assets (e.g., code, data, models) are used, does the paper cite the creators and respect the license and terms of use?",
        "If new assets are released, does the paper document them and provide relevant details (training, license, limitations, etc.) alongside the assets?",
        "If crowdsourcing was used or research was conducted with human subjects, does the paper include the full text of instructions given to participants, screenshots (if applicable), and compensation details?",
        "If research involved human subjects, does the paper describe potential participant risks and confirm that IRB approval (or equivalent) was obtained?",
        "If LLMs are used as an important, original, or non-standard component of the core methods, does the paper describe that usage?",
    ]

    for i, text in enumerate(questions):
        Question.objects.create(conference=conference, question_text=text, position=i)


def remove_conference_NeurIPS_questions(apps, schema_editor):
    Conference = apps.get_model('paper_grader', 'Conference')
    Question = apps.get_model('paper_grader', 'Question')

    try:
        conference = Conference.objects.get(name='NeurIPS')
        Question.objects.filter(conference=conference).delete()
    except Conference.DoesNotExist:
        pass

class Migration(migrations.Migration):

    dependencies = [
        ('paper_grader', '0005_alter_conference_name'),
    ]

    operations = [
        migrations.RunPython(add_conference_NeurIPS_questions, remove_conference_NeurIPS_questions),

    ]

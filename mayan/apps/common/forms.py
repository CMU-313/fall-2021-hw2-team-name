from mayan.apps.views.forms import FileDisplayForm
from django import forms

# Dropdown choices
experience_score_choices = skills_score_choices = (
    ("1", "One"),
    ("2", "Two"),
    ("3", "Three"),
    ("4", "Four"),
    ("5", "Five"),
)

gpa_score_choices = (
    ("1", "1: (0.00 to 0.99)"),
    ("2", "2: (1.00 to 1.99)"),
    ("3", "3: (2.00 to 2.99)"),
    ("4", "4: (3.00 to 3.49)"),
    ("5", "5: (3.50 to 4.00)"),
)

essay_score_choices = (
    ("1", "1: (beginner)"),
    ("2", "2: (satisfactory)"),
    ("3", "3: (average)"),
    ("4", "4: (proficient)"),
    ("5", "5: (excellent)"),
)

final_decision_choices = (
    ("1", "Yes"),
    ("2", "No"),
)

class LicenseForm(FileDisplayForm):
    DIRECTORY = ()
    FILENAME = 'LICENSE'

# Structure of the reviewer form for a candidate
class ReviewerForm(forms.Form):
    # Source: https://github.com/wagtail/wagtail/issues/130
    # This Github post explained how to remove the extra colon when a form
    # field was created by Django
    def __init__(self, *args, **kwargs):
        kwargs.setdefault('label_suffix', '')  # globally override the Django >=1.6 default of ':'
        super(ReviewerForm, self).__init__(*args, **kwargs)

    ################################################################ 
    #### Fields
    ################################################################
    
    first_name = forms.CharField(max_length=25, required=True)
    last_name = forms.CharField(max_length=25, required=True)
    email = forms.EmailField(max_length=50, label="Email Address", required=True)
    
    experience_score = forms.ChoiceField(choices=experience_score_choices, label="Experience Score:", required=True)
    skills_score = forms.ChoiceField(choices=skills_score_choices, label="Skill Score:", required=True)
    gpa_score = forms.ChoiceField(choices=gpa_score_choices, label="GPA Score:", required=True)
    essay_score = forms.ChoiceField(choices=essay_score_choices, label="Essay Score:", required=True)

    additional_comments = forms.CharField(widget=forms.Textarea, label="Additional Comments:", required=True)
    reviewer_name = forms.CharField(max_length=50, label="Reviewer Name", required=True)

    final_decision = forms.ChoiceField(choices=final_decision_choices, label="Final Decision:", required=True)

    ################################################################ 
    #### Widgets
    ################################################################
    
    # Candidate's first name
    first_name.widget.attrs.update({'id': 'candidate-first-name'})
    
    # Candidate's last name
    last_name.widget.attrs.update({'id': 'candidate-last-name'})
    
    # Candidate's email address
    email.widget.attrs.update({'id': 'candidate-email'})

    # Candidate's experience score
    experience_score.widget.attrs.update({'id': 'candidate-experience-score'})

    # Candidate's experience score
    skills_score.widget.attrs.update({'id': 'candidate-skills-score'})

    # Candidate's GPA score
    gpa_score.widget.attrs.update({'id': 'candidate-gpa-score'})

    # Candidate's essay score
    essay_score.widget.attrs.update({'id': 'candidate-essay-score'})

    # Reviewer's additional comments
    additional_comments.widget.attrs.update({'id': 'reviewer-additional-comments'})

    # Name of reviewer
    reviewer_name.widget.attrs.update({'id': 'reviewer-name'})

    # Final decision for acceptance or denial for the candidate
    final_decision.widget.attrs.update({'id': 'reviewer-final-decision'})

    ################################################################ 
    #### Form Validation
    ################################################################

    # Each function below validates a given form input

    def clean_experience_score(self):
        data = self.cleaned_data.get['experience_score']
        possible_scores = ["One", "Two", "Three", "Four", "Five"]

        if data not in possible_scores:
            raise forms.ValidationError("ERROR: Invalid Experience Score.")

    def clean_skills_score(self):
        data = self.cleaned_data.get['experience_score']
        possible_scores = ["One", "Two", "Three", "Four", "Five"]

        if data not in possible_scores:
            raise forms.ValidationError("ERROR: Invalid Skills Score.")

    def clean_gpa_score(self):
        data = self.cleaned_data.get['experience_score']
        possible_scores = ["1: (0.00 to 0.99)", "2: (1.00 to 1.99)", "3: (2.00 to 2.99)",
                           "4: (3.00 to 3.49)", "5: (3.50 to 4.00)"]

        if data not in possible_scores:
            raise forms.ValidationError("ERROR: Invalid GPA Score.")

    def clean_essay_score(self):
        data = self.cleaned_data.get['experience_score']
        possible_scores = ["1: (beginner)", "2: (satisfactory)", "3: (average)",
                           "4: (proficient)", "5: (excellent)"]

        if data not in possible_scores:
            raise forms.ValidationError("ERROR: Invalid Essay Score.")

    def clean_final_decision(self):
        data = self.cleaned_data.get['experience_score']
        possible_scores = ["1", "Yes", "2", "No"]

        if data not in possible_scores:
            raise forms.ValidationError("ERROR: Invalid Final Decision.")

    # Clean function that calls on the super class clean function and has additional
    # validation checks added by the developer.
    def clean(self):
        cleaned_data = super().clean()

        # Add additional validation checks here        
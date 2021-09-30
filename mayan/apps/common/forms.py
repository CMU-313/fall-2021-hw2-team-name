from mayan.apps.views.forms import FileDisplayForm
from django import forms

# Dropdown choices
experience_score_choices = (
    ("1", "One"),
    ("2", "Two"),
    ("3", "Three"),
    ("4", "Four"),
    ("5", "Five"),
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
    
    first_name = forms.CharField(max_length=25, label='First Name')
    last_name = forms.CharField(max_length=25)
    email = forms.EmailField(max_length=50, required=True)
    
    experience_score = forms.ChoiceField(choices=experience_score_choices)

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
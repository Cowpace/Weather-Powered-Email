from django.forms import Form
from django.forms.fields import EmailField, ChoiceField
from django.forms.widgets import EmailInput, ChoiceWidget


class MainForm(Form):
    email = EmailField(widget=EmailInput())
    location = ChoiceField(choices=((1, 'Boston, MA'), (2, 'Orlando, FL')))

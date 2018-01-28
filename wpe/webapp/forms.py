from django.forms import Form
from django.forms.fields import EmailField, ChoiceField
from django.forms.widgets import EmailInput

from webapp.models import WeatherModel


class MainForm(Form):
    """A form for the email and location, with the locations sorted alphabetically"""
    email = EmailField(widget=EmailInput())
    location = ChoiceField()

    def __init__(self, *args, **kwargs):
        super(MainForm, self).__init__(*args, **kwargs)
        locations = sorted(
            '{}, {}'.format(model.city, model.state)
            for index, model in enumerate(WeatherModel.objects.all())
        )
        self.fields['location'].choices = (
            (index, location)
            for index, location in enumerate(locations)
        )

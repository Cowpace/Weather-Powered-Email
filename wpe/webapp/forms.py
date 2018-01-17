from django.forms import Form
from django.forms.fields import EmailField, ChoiceField
from django.forms.widgets import EmailInput

from webapp.models import WeatherModel


class MainForm(Form):
    email = EmailField(widget=EmailInput())
    location = ChoiceField()

    def __init__(self, *args, **kwargs):
        super(MainForm, self).__init__(*args, **kwargs)
        self.fields['location'].choices = (
            (index, '{}, {}'.format(model.city, model.state))
            for index, model in enumerate(WeatherModel.objects.all())
        )

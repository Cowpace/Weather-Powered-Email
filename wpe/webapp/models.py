import csv, os
from django.db import models

from .wunderground_client import WundergoundClient
from wpe.settings import BASE_DIR


class EmailSignupModel(models.Model):
    """A model for the MainForm class"""
    email = models.EmailField(primary_key=True, unique=True)
    city = models.TextField()
    state = models.TextField()

    def __init__(self, *args, **kwargs):
        super(EmailSignupModel, self).__init__(*args, **kwargs)
        self._wunderground_client = WundergoundClient()

    def get_past_temp(self):
        return self._wunderground_client.get_last_year_temp(self.city, self.state)

    def get_current_weather(self):
        return self._wunderground_client.get_current_weather(self.city, self.state)


class WeatherModel(models.Model):
    """A model for caching weather data on cities and states. Assumes every city is unique regardless of state"""
    city = models.TextField(primary_key=True)
    state = models.TextField()
    current_weather = models.TextField(null=True)
    current_tempurature = models.FloatField(null=True)
    past_tempurature = models.FloatField(null=True)

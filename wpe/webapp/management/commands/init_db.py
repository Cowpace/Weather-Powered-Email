import csv, os
from django.core.management.base import BaseCommand

from webapp.models import WeatherModel
from wpe.settings import BASE_DIR


class Command(BaseCommand):
    def handle(self, *args, **options):
        """Load the top 100 cities by population from an edited csv that was
        originally found here:

        https://simplemaps.com/data/us-cities
        """
        city_and_states = []
        with open(os.path.join(BASE_DIR, 'webapp/resources/top100-cities.csv')) as file:
            reader = csv.reader(file)
            for row in reader:
                city, state, *_ = row
                city_and_states.append((city, state))

        for city, state in city_and_states:
            WeatherModel.objects.update_or_create(
                city=city,
                state=state
            )

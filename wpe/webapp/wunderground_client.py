import requests
from datetime import datetime, timedelta

from wpe.settings import API_KEY


class WundergoundClient(object):
    BASE_URL = 'http://api.wunderground.com/api/{api_key}/{route}/q/{state}/{city}.json'

    def _execute(self, route, city, state):
        return requests.get(
            self.BASE_URL.format(
                api_key=API_KEY,
                route=route,
                city=city,
                state=state
            )
        ).json()

    def get_current_weather(self, city, state):
        route = 'conditions'
        raw_json = self._execute(route, city, state)
        observations = raw_json['current_observation']
        print(observations)
        return float(observations['temp_f'])

    def get_last_year_temp(self, city, state):
        """get last years tempurature at this hour in the given city and state"""
        route = 'history_{date}'
        lookback = datetime.today() - timedelta(days=365)
        current_hour = datetime.now().hour

        route = route.format(date=lookback.strftime("%Y%m%d"))

        raw_json = self._execute(route, city, state)

        observations = raw_json['history']['observations']
        return float(observations[current_hour]['tempi'])
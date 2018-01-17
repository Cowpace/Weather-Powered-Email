import requests, traceback
from requests import HTTPError
from datetime import datetime, timedelta

from wpe.settings import API_KEY


class WundergoundClient(object):
    BASE_URL = 'http://api.wunderground.com/api/{api_key}/{route}/q/{state}/{city}.json'

    def _execute(self, route, city, state):
        response = requests.get(
            self.BASE_URL.format(
                api_key=API_KEY,
                route=route,
                city=city,
                state=state
            )
        )
        if response.status_code != 200:
            response.raise_for_status()
        return response.json()

    def get_current_weather(self, city, state):
        route = 'conditions'
        try:
            raw_json = self._execute(route, city, state)
        except HTTPError:
            # log (print) the exception and dont block downstream processing
            print(traceback.format_exc())
            return None, None
        observations = raw_json['current_observation']
        return float(observations['temp_f']), observations['weather']

    def get_last_year_temp(self, city, state):
        """get last years tempurature at this hour in the given city and state"""
        route = 'history_{date}'
        lookback = datetime.today() - timedelta(days=365)
        current_hour = datetime.now().hour

        route = route.format(date=lookback.strftime("%Y%m%d"))

        try:
            raw_json = self._execute(route, city, state)
        except HTTPError:
            # log (print) the exception and dont block downstream processing
            print(traceback.format_exc())
            return None

        observations = raw_json['history']['observations']
        return float(observations[current_hour]['tempi'])
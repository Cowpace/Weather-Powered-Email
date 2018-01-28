import requests, traceback
from requests import HTTPError
from datetime import datetime, timedelta

from wpe.settings import API_KEY


class WundergoundClient(object):
    """A wrapper around requests that calls the wunderground API

    Side note: Some of the trickier city names like "Winston-Salem" and "North Las Vegas" seem to play nice with
        the API, and since I cant verify if a given city is supported per
        (https://apicommunity.wunderground.com/weatherapi/topics/list-of-cities-that-can-be-called-through-api)
        im going to assume for simplicity that any city passed is valid.
    """
    BASE_URL = 'http://api.wunderground.com/api/{api_key}/{route}/q/{state}/{city}.json'

    def _execute(self, route, city, state):
        """Calls the api and returns the response as a dict

        Args:
            route (str): the subroute to call in the api. such as "conditions" or "history_20170101"
            city (str): the city to get the route for
            state (str): the two character state abbreviation to get the route for

        Returns:
            dict: The response from the API

        Raises:
            HTTPError
        """
        response = requests.get(
            self.BASE_URL.format(
                api_key=API_KEY,
                route=route,
                city=city,
                state=state.upper()
            )
        )
        if response.status_code != 200:
            response.raise_for_status()
        return response.json()

    def get_current_weather(self, city, state):
        """Gets the current weather and the current temperature in fahrenheit for the given city and state

        Args:
            city (str): the city
            state (str): the two character state abbreviation

        Returns:
            tuple of float, str: The current temperature in fahrenheit and a phrase describing the current weather,
                such as "sunny" or "snow"
        """
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
        """Gets the temperature in fahrenheit for the given city and state from one year ago from the same hour

        Args:
            city (str): the city
            state (str): the two character state abbreviation

        Returns:
            float: The temperature from one year ago in fahrenheit
        """
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
import smtplib, os
from urllib import request
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage

from django.core.management.base import BaseCommand
from giphypop import Giphy

from webapp.models import EmailSignupModel, WeatherModel
from wpe.settings import BASE_DIR, EMAIL_USER, EMAIL_PASSWORD


class Command(BaseCommand):
    def handle(self, *args, **options):
        """Loops through the records from the EmailSignupModel and sends a personalized email based on
        the weather from the same time one year ago, and includes a giphy of the current weather
        """
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server.ehlo()
        server.login(EMAIL_USER, EMAIL_PASSWORD)

        models = EmailSignupModel.objects.all()

        cache_of_temps = {}
        if options.get('--use-cache', None):
            cache_of_temps = self._load_weather_stats()

        for model in models:
            # memoize the wunderground API calls, since the developer licence has a limit on the calls per minute
            if (model.city, model.state) not in cache_of_temps:
                current_temp, current_weather = model.get_current_weather()
                cache_of_temps[(model.city, model.state)] = model.get_past_temp(), current_temp, current_weather

            past_temp, current_temp, current_weather = cache_of_temps[(model.city, model.state)]
            # make sure that the client returned a 200 response for both
            if current_temp and past_temp:
                # assume that last years temp is good enough for an average for this time of year
                temp_delta = current_temp - past_temp
            else:
                # otherwise default to a normal email
                temp_delta = 0

            sent_from = 'Weather Powered Email'
            message = self._build_email(
                model.email,
                sent_from,
                current_temp,
                current_weather,
                temp_delta,
                model.city,
                model.state
            )
            server.sendmail(sent_from, model.email, message)

        server.close()
        self._save_weather_stats(cache_of_temps)

    def add_arguments(self, parser):
        """allow a use cache param to use data from the WeatherModels instead of using API calls"""
        parser.add_argument('--use-cache', nargs='*', type=bool)

    def _build_email(self, to_email, from_email, temp, weather, temp_delta, city, state):
        """Builds a personalized email based on the current weather, and how it compares to the weather from one
        year ago in a given city and state

        Args:
            to_email (str): the email address this is being sent to
            from_email (str): the email address this is being sent from
            temp (str): the current temperature of the given city, in fahrenheit
            weather (str): A phrase describing the current weather. Such as "partly cloudy" or "sunny"
            temp_delta (float): the difference in temperature between now, and exactly one year ago in the given city
            city (str): The city name of the temperature data
            state (str): The two character state abbreviation of the given city

        Returns:
            str: The email to send, as a string
        """
        giphy = Giphy()
        if temp_delta > 5:
            subject = "It's nice out! Enjoy a discount on us."
        elif temp_delta < 5:
            subject = "Not so nice out? That's okay, enjoy a discount on us."
        else:
            subject = "Enjoy a discount on us."

        body = '{} degrees, {} in {}, {}'.format(int(temp), weather, city, state)

        msg = MIMEMultipart()
        msg["To"] = to_email
        msg["From"] = from_email
        msg["Subject"] = subject

        # stick weather at the end and hope giphy behaves
        image = giphy.translate(phrase='{} weather'.format(weather))
        image_dir = os.path.join(BASE_DIR, 'webapp/resources/image.gif')
        request.urlretrieve(image.media_url, image_dir)

        msgText = MIMEText('<b>%s</b><br><img src="cid:%s"><br>' % (body, image_dir), 'html')
        msg.attach(msgText)

        # Doing file io here isnt great, but im not sure how to get the html in the email to play nice
        fp = open(image_dir, 'rb')
        img = MIMEImage(fp.read())
        fp.close()
        img.add_header('Content-ID', '<{}>'.format(image_dir))
        msg.attach(img)
        return msg.as_string()

    def _save_weather_stats(self, temperatures):
        """Saves temperature data for a given set of cities to the database so they can be used later if needed,
        to help minimize the calls on the wunderground API

        Args:
            temperatures (dict of tuple, tuple): A mapping of cities and state abbreviation to a tuple of three elements
                relating to the weather in that city and state. The temperature from one year ago, the current
                temperature, and a string describing the current weather, such as "partly cloudy" or "sunny"
        """
        for (city, state), (past_temp, current_temp, current_weather) in temperatures.items():
            model = WeatherModel.objects.get(
                city=city,
                state=state
            )
            model.current_weather = current_weather
            model.past_tempurature = past_temp
            model.current_tempurature = current_temp
            model.save()

    def _load_weather_stats(self):
        """Loads the WeatherModel objects from the database as a dict

        Returns:
            dict of tuple, tuple: A mapping of cities and state abbreviation to a tuple of three elements
                relating to the weather in that city and state. The temperature from one year ago, the current
                temperature, and a string describing the current weather, such as "partly cloudy" or "sunny"
        """
        models = WeatherModel.objects.all()
        result = {}
        for model in models:
            if model.current_weather and model.past_weather:
                item = model.past_tempurature, model.current_tempurature, model.current_weather
                result[(model.city, model.state)] = item
        return result
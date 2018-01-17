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
    def _build_email(self, to_email, from_email, temp, weather, temp_delta, city, state):
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

    def _save_weather_stats(self, tempuratures):
        for (city, state), (past_temp, current_temp, current_weather) in tempuratures.items():
            model = WeatherModel.objects.get(
                city=city,
                state=state
            )
            model.current_weather = current_weather
            model.past_tempurature = past_temp
            model.current_tempurature = current_temp
            model.save()

    def _load_weather_stats(self):
        models = WeatherModel.objects.all()
        result = {}
        for model in models:
            if model.current_weather and model.past_weather:
                item = model.past_tempurature, model.current_tempurature, model.current_weather
                result[(model.city, model.state)] = item
        return result

    def handle(self, *args, **options):
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server.ehlo()
        server.login(EMAIL_USER, EMAIL_PASSWORD)

        models = EmailSignupModel.objects.all()

        cache_of_temps = {}
        if options.get('--use-cache', None):
            cache_of_temps = self._load_weather_stats()

        for model in models:
            # memoize the wunderground API calls
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
        parser.add_argument('--use-cache', nargs='*', type=bool)
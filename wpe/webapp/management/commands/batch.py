import os, smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from django.core.management.base import BaseCommand

from ...models import EmailSignupModel, WeatherModel
from wpe.settings import BASE_DIR, EMAIL_USER, EMAIL_PASSWORD


class Command(BaseCommand):
    def _build_email(self, to_email, from_email, temp, temp_delta, city, state):
        img_path = os.path.join(BASE_DIR, 'webapp/resources/')

        if temp_delta > 5:
            subject = "It's nice out! Enjoy a discount on us."
            attachment = os.path.join(img_path, 'good_weather.jpg')
        elif temp_delta < 5:
            subject = "Not so nice out? That's okay, enjoy a discount on us."
            attachment = os.path.join(img_path, 'bad_weather.jpg')
        else:
            subject = "Enjoy a discount on us."
            attachment = os.path.join(img_path, 'average_weather.jpg')

        body = 'It\'s {} degrees in {}, {}'.format(int(temp), city, state)

        msg = MIMEMultipart()
        msg["To"] = to_email
        msg["From"] = from_email
        msg["Subject"] = subject

        msgText = MIMEText('<b>%s</b><br><img src="cid:%s"><br>' % (body, attachment), 'html')
        msg.attach(msgText)

        fp = open(attachment, 'rb')
        img = MIMEImage(fp.read())
        fp.close()
        img.add_header('Content-ID', '<{}>'.format(attachment))
        msg.attach(img)
        return msg.as_string()

    def _save_weather_stats(self, tempuratures):
        for (city, state), (past_temp, current_temp) in tempuratures.items():
            WeatherModel.objects.update_or_create(
                city=city,
                state=state,
                current_tempurature=current_temp,
                past_tempurature=past_temp
            )

    def _load_weather_stats(self):
        models = WeatherModel.objects.all()
        result = {}
        for model in models:
            if model.current_weather and model.past_weather:
                result[(model.city, model.state)] = model.past_weather, model.current_weather
        return result

    def handle(self, *args, **options):
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server.ehlo()
        server.login(EMAIL_USER, EMAIL_PASSWORD)

        models = EmailSignupModel.objects.all()

        cache_of_temps = {}
        if not options.get('--flush-cache', None):
            cache_of_temps = self._load_weather_stats()

        for model in models:
            if (model.city, model.state) not in cache_of_temps:
                cache_of_temps[(model.city, model.state)] = model.get_past_temp(), model.get_current_temp()

            past_temp, current_temp = cache_of_temps[(model.city, model.state)]
            temp_delta = current_temp - past_temp

            sent_from = 'Weather Powered Email'
            message = self._build_email(
                model.email,
                sent_from,
                current_temp,
                temp_delta,
                model.city,
                model.state
            )
            server.sendmail(sent_from, model.email, message)

        server.close()

        self._save_weather_stats(cache_of_temps)

    def add_arguments(self, parser):
        parser.add_argument('--flush-cache', nargs='*', type=bool)
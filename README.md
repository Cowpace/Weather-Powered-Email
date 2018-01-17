# Weather-Powered-Email

A simple Django app that signs users up for emails related to the weather in their area, and sends them giphys based on
the current weather conditions.

You can execute the batch emailing by running the django management command `batch`

Based on the challange from here:
https://www.klaviyo.com/weather-app

To setup, set the following enviorment variables:
`API_KEY`: The API key for the wunderground api
`EMAIL_USER`: The email user to use for sending emails
`EMAIL_PASSWORD`: The email user's password

And then run the django management command `init_db` to build out the cities used in the location dropdown on the app

Built using:
https://simplemaps.com/data/us-cities
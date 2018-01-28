# Weather-Powered-Email

A simple Django app that signs users up for emails related to the weather in their area, and sends them giphys based on
the current weather conditions.

Based on the challange from here:
https://www.klaviyo.com/weather-app

To setup (assuming your on linux), open a terminal and git clone the repo into a directory and then
set the following enviorment variables:

`API_KEY`: The API key for the wunderground api (mine is 8de8292e7a75ba85, while usually you never ever want to check in
api keys into git, I dont think its an issue for this coding challenge)

`EMAIL_USER`: The email user to use for sending emails

`EMAIL_PASSWORD`: The email user's password

set these using:

```
export API_KEY={key};
export EMAIL_USER={user};
export EMAIL_PASSWORD={password};
```

Now navigate `directory-where-you-git-cloned-the-repo/Weather-Powered-Email`

first, assert you have python 3.6 on your machine, and then activate the virtual env

`source venv/bin/activate`

Then you will need to populate the DB with cities and states. first `cd wpe` and then:

`python manage.py init_db`

Now you can start the server using `python manage.py runserver` and input emails to subscribe them

To send emails to subscribed users, from the `Weather-Powered-Email/wpe` directory, run:

`python manage.py batch`

This should send emails per the spec in the challange doc to the subscribed users, with a Giphy of the current weather

Built using:
https://simplemaps.com/data/us-cities
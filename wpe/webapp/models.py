from django.db import models


# Create your models here.
class EmailSignupModel(models.Model):
    email = models.EmailField()
    location = models.IntegerField()

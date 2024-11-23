from django.db import models

# Create your models here.
class User(models.Model):
    name = models.CharField(max_length=30, blank=False, null=False)
    surname = models.CharField(max_length=40, blank=False, null=False)
    number = models.IntegerField(unique=True)
    email = models.EmailField(max_length=100, unique=True)
    password = models.CharField(max_length=50)
    residential_address = models.CharField(max_length=100)
    profile_pic = models.CharField(max_length=255, unique=True)
    
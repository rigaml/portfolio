from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    # Forces the User email to be unique in the database
    email = models.EmailField(unique=True)
    
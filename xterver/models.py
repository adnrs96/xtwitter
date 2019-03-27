from django.contrib.auth.models import AbstractBaseUser
from django.db import models

class UserProfile(AbstractBaseUser):
    USERNAME_FIELD = 'username'
    email = models.EmailField(blank=False, unique=True)
    username = models.CharField(max_length=40, unique=True)

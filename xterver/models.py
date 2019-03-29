from django.contrib.auth.models import AbstractBaseUser, UserManager
from django.db import models

class UserProfile(AbstractBaseUser):
    USERNAME_FIELD = 'username'
    MAX_NAME_LENGTH = 100
    email = models.EmailField(blank=False, unique=True)
    username = models.CharField(max_length=40, unique=True)
    full_name = models.CharField(max_length=MAX_NAME_LENGTH)
    follower_count = models.PositiveIntegerField(default=0)
    following_count = models.PositiveIntegerField(default=0)
    objects = UserManager()

class UserConfirmation(models.Model):
    full_name = models.CharField(blank=False, max_length=UserProfile.MAX_NAME_LENGTH)
    email = models.EmailField(blank=False, unique=True)
    is_confirmed = models.BooleanField(blank=False, default=False)
    confirmation_key = models.CharField(blank=False, max_length=6)

class Connection(models.Model):
    follower_userprofile = models.ForeignKey(UserProfile,
                                             related_name='following',
                                             blank=False,
                                             on_delete=models.CASCADE)
    following_userprofile = models.ForeignKey(UserProfile,
                                              related_name='followers',
                                              blank=False,
                                              on_delete=models.CASCADE)

    class Meta:
        unique_together = ("follower_userprofile", "following_userprofile")

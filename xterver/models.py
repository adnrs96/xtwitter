from django.contrib.auth.models import AbstractBaseUser, UserManager
from django.db import models
from django.utils.timezone import now as timezone_now

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

class Xtweet(models.Model):
    creator = models.ForeignKey(UserProfile,
                                related_name='+',
                                blank=False,
                                on_delete=models.CASCADE)
    content = models.TextField()
    rendered_content = models.TextField(null=True)
    likes_count = models.PositiveIntegerField(default=0)
    retweets_count = models.PositiveIntegerField(default=0)
    replies_count = models.PositiveIntegerField(default=0)

class UserXtweet(models.Model):
    user = models.ForeignKey(UserProfile,
                             related_name='xtweets',
                             blank=False,
                             on_delete=models.CASCADE)
    xtweet = models.ForeignKey(Xtweet,
                               related_name='+',
                               null=True,
                               on_delete=models.CASCADE)
    parent_xtweet = models.ForeignKey(Xtweet,
                                      related_name='replies',
                                      null=True,
                                      on_delete=models.CASCADE)
    is_retweet = models.BooleanField(default=False)
    is_reply = models.BooleanField(default=False)
    publish_datetime = models.DateTimeField(default=timezone_now)
    is_deleted = models.BooleanField(default=False)

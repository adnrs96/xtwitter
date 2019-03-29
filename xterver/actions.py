from xterver.models import UserProfile, UserConfirmation, Connection
from django.contrib.auth.models import UserManager
from typing import List
import string
import random

def do_check_username_used(username: str) -> bool:
    return UserProfile.objects.filter(username=username).exists()

def do_check_email_registered(email: str) -> bool:
    return UserProfile.objects.filter(email=email).exists()

def do_check_email_in_confirmation(email: str) -> bool:
    return UserConfirmation.objects.filter(email=email).exists()

def do_create_user(full_name: str, username:str, email: str, password: str) -> UserProfile:
    user_profile = UserProfile(email=UserManager.normalize_email(email),
                               full_name=full_name,
                               username=username)
    user_profile.set_password(password)
    user_profile.save()
    return user_profile

def make_confirmation_key(size: int=6,
                          chars: List[str]=string.ascii_uppercase + string.digits) -> str:
    return ''.join(random.choice(chars) for _ in range(size))

def do_register_user_for_confirmation(email: str, full_name: str) -> str:
    confirmation_key = make_confirmation_key()
    user_confirmation = UserConfirmation(email=UserManager.normalize_email(email),
                                         full_name=full_name,
                                         is_confirmed=False,
                                         confirmation_key=confirmation_key)
    user_confirmation.save()
    return confirmation_key

def get_user_confirmation(email: str) -> UserConfirmation:
    return UserConfirmation.objects.filter(email=email).first()

def get_user_by_email(email: str) -> UserProfile:
    return UserProfile.objects.filter(email=email).first()

def get_user_by_username(username: str) -> UserProfile:
    return UserProfile.objects.filter(username=username).first()

def do_check_user_follows_user(follower: UserProfile, following: UserProfile) -> bool:
    return follower.following.filter(following_userprofile=following).exists()

def do_create_connection(follower: UserProfile, following: UserProfile) -> Connection:
    connection = Connection(follower_userprofile=follower,
                             following_userprofile=following)
    connection.save()
    return connection

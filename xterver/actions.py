from xterver.models import UserProfile, UserConfirmation
from django.contrib.auth.models import UserManager
from django.utils import timezone
from typing import List
import string
import random

def do_make_unique_user_name(email: str) -> str:
    # TODO: Make usernames meaningfull.
    return str(timezone.now())

def do_check_username_used(username: str) -> bool:
    return UserProfile.objects.filter(username=username).exists()

def do_check_email_registered(email: str) -> bool:
    return UserProfile.objects.filter(email=email).exists()

def do_check_email_in_confirmation(email: str) -> bool:
    return UserConfirmation.objects.filter(email=email).exists()

def do_create_user(full_name: str, email: str, password: str) -> str:
    username = do_make_unique_user_name(email)
    user_profile = UserProfile(email=UserManager.normalize_email(email),
                               full_name=full_name,
                               username=username,
                               password=password)
    user_profile.save()
    return username

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
    return UserConfirmation.objects.get(email=email)

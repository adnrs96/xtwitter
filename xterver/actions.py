from xterver.models import UserProfile
from django.contrib.auth.models import UserManager
from django.utils import timezone

def do_make_unique_user_name(email: str) -> str:
    # TODO: Make usernames meaningfull.
    return str(timezone.now())

def do_check_username_used(username: str) -> bool:
    return UserProfile.objects.filter(username=username).exists()

def do_check_email_used(email: str) -> bool:
    return UserProfile.objects.filter(email=email).exists()

def do_create_user(email: str, password: str) -> str:
    username = do_make_unique_user_name(email)
    user_profile = UserProfile(email=UserManager.normalize_email(email),
                               username=username,
                               password=password)
    user_profile.save()
    return username

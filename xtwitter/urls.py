"""xtwitter URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from xterver.views.registeration import (
    pre_registeration, final_registeration, confirm_registeration,
    authenticate_and_login, logout_view
)
from xterver.views.users import (
    handle_follow_user
)
from xterver.views.xtweets import (
    handle_xtweet_creation, handle_xtweet_read
)

urlpatterns = [
    path('accounts/new', pre_registeration),
    path('accounts/confirm', confirm_registeration),
    path('accounts', final_registeration),
    path('login', authenticate_and_login),
    path('logout', logout_view),
    path('users/<slug:username>/follow', handle_follow_user),
    path('<slug:username>/xtweets', handle_xtweet_creation),
    path('<slug:username>/xtweets/<int:xtweet_id>', handle_xtweet_read),
]

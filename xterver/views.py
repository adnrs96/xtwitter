from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth import authenticate, login
from rest_framework.decorators import api_view
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import render
from django.core import validators
from django.core.exceptions import ValidationError
from xterver.lib.response import json_response
from xterver.serializers import UserProfileSerializer, UserConfirmationSerializer
from xterver.actions import (
    do_check_email_in_confirmation, do_create_user, do_register_user_for_confirmation,
    do_check_email_registered, get_user_confirmation, get_user_by_email
)

@csrf_exempt
@api_view(['POST'])
def confirm_registeration(request: Request) -> Response:
    """
    Confirms User email.
    """
    if request.method == "POST":
        email = request.data.get('email', None)
        key = request.data.get('key', None)
        if email is None or key is None:
            return Response(json_response('error', 'Missing Email or Key'),
                            status=status.HTTP_400_BAD_REQUEST)
        try:
            validators.validate_email(email)
        except ValidationError:
            return Response(json_response('error', 'Invalid Email'),
                            status=status.HTTP_400_BAD_REQUEST)
        user_confirmation = get_user_confirmation(email)
        if not user_confirmation:
            return Response(json_response('error', 'No Such User Registered for Confirmation.'),
                            status=status.HTTP_404_NOT_FOUND)
        if user_confirmation.is_confirmed:
            return Response(json_response('error', 'Email Already Confirmed.'),
                            status=status.HTTP_417_EXPECTATION_FAILED)
        if user_confirmation.confirmation_key != key:
            return Response(json_response('error', 'Confirmation Key did not match.'),
                            status=status.HTTP_401_UNAUTHORIZED)
        user_confirmation.is_confirmed = True
        user_confirmation.save(update_fields=['is_confirmed'])
        return Response(json_response('success',
                        'User Email Confirmed.'),
                        status=status.HTTP_200_OK)

@csrf_exempt
@api_view(['POST'])
def pre_registeration(request: Request) -> Response:
    """
    Registers a user for email confirmation.
    """
    if request.method == "POST":
        user_confirmation = UserConfirmationSerializer(data=request.data)
        if not user_confirmation.is_valid():
            return Response(json_response('error', user_confirmation.errors),
                            status=status.HTTP_400_BAD_REQUEST)
        validated_data = user_confirmation.validated_data
        full_name = validated_data.get('full_name')
        email = validated_data.get('email')
        try:
            validators.validate_email(email)
        except ValidationError:
            return Response(json_response('error', 'Invalid Email'),
                            status=status.HTTP_400_BAD_REQUEST)
        if do_check_email_registered(email):
            return Response(json_response('error', 'Email already in use.'),
                            status=status.HTTP_400_BAD_REQUEST)
        confirmation_key = do_register_user_for_confirmation(email, full_name)
        # TODO: Send user a confirmation email
        return Response(json_response('success',
                        'User Preregisteration complete. Confirmation Email Sent.'),
                        status=status.HTTP_200_OK)

@csrf_exempt
@api_view(['POST'])
def final_registeration(request: Request) -> Response:
    """
    Registers a new user with unique email and password.
    """
    if request.method == "POST":
        user_profile_serialized = UserProfileSerializer(data=request.data)
        if not user_profile_serialized.is_valid():
            return Response(json_response('error', user_profile_serialized.errors),
                            status=status.HTTP_400_BAD_REQUEST)
        validated_data = user_profile_serialized.validated_data
        email = validated_data.get('email')
        password = validated_data.get('password')
        try:
            validators.validate_email(email)
        except ValidationError:
            return Response(json_response('error', 'Invalid Email'),
                            status=status.HTTP_400_BAD_REQUEST)
        user_confirmation = get_user_confirmation(email)
        if user_confirmation is None:
            return Response(json_response('error', 'No such user registered for confirmation.'),
                            status=status.HTTP_400_BAD_REQUEST)
        try:
            validate_password(password)
        except ValidationError as e:
            return Response(json_response('error', e),
                            status=status.HTTP_400_BAD_REQUEST)
        if not user_confirmation.is_confirmed:
                return Response(json_response('error', 'Email Id Confirmation pending.'),
                                status=status.HTTP_400_BAD_REQUEST)
        user = do_create_user(user_confirmation.full_name, email, password)
        login(request, user)
        return Response(json_response('success', 'User Created.',
                        data={'username': user.username}),
                        status=status.HTTP_201_CREATED)
        return Response(request.data)

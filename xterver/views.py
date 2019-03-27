from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.password_validation import validate_password
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
    do_check_email_registered
)

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
        if do_check_email_in_confirmation(email):
            return Response(json_response('error', 'Email already in use.'),
                            status=status.HTTP_400_BAD_REQUEST)
        try:
            validate_password(password)
        except ValidationError as e:
            return Response(json_response('error', e),
                            status=status.HTTP_400_BAD_REQUEST)
        username_created = do_create_user(email, password)
        return Response(json_response('success', 'User Created.',
                        data={'username': username_created}),
                        status=status.HTTP_201_CREATED)
        return Response(request.data)

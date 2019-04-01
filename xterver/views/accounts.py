from django.contrib.auth import login, logout
from rest_framework.decorators import api_view
from rest_framework.request import Request
from rest_framework.response import Response
from xterver.lib.response import json_response
from rest_framework import status
from xterver.actions import get_user_by_email

@api_view(['POST'])
def authenticate_and_login(request):
    potential_user = get_user_by_email(request.data.get('email', ''))
    if potential_user is None:
        return Response(json_response('error', 'Invalid Email or Password.'),
                        status=status.HTTP_400_BAD_REQUEST)
    authenticated = potential_user.check_password(request.data.get('password', ''))
    if authenticated:
        login(request, potential_user)
        return Response(json_response('success', 'Logged In'),
                        status=status.HTTP_200_OK)
    return Response(json_response('error', 'Invalid Email or Password.'),
                    status=status.HTTP_400_BAD_REQUEST)

@api_view(['DELETE'])
def logout_view(request):
    logout(request)
    return Response(json_response('success', 'Logged Out.'),
                    status=status.HTTP_200_OK)

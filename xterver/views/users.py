from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.transaction import TransactionManagementError
from rest_framework.decorators import api_view
from rest_framework.request import Request
from rest_framework.response import Response
from xterver.lib.response import json_response
from xterver.lib.response import json_response
from rest_framework import status
from xterver.actions import (
    get_user_by_username, do_check_user_follows_user, do_create_connection
)

@login_required(login_url='/login')
@api_view(['PUT'])
def handle_follow_user(request: Request, username: str) -> Response:
    if request.method == 'PUT':
        user_to_follow = get_user_by_username(username)
        if user_to_follow is None:
            return Response(json_response('error', 'Invalid username.'),
                            status=status.HTTP_404_NOT_FOUND)
        if request.user == user_to_follow:
            return Response(json_response('error', 'Operation not allowed on oneself.'),
                            status=status.HTTP_403_FORBIDDEN)
        if do_check_user_follows_user(request.user, user_to_follow):
            return Response(json_response('error', 'User is already a follower.'),
                            status=status.HTTP_400_BAD_REQUEST)
        try:
            with transaction.atomic():
                do_create_connection(request.user, user_to_follow)
                request.user.following_count += 1
                user_to_follow.follower_count += 1
                request.user.save(update_fields=['following_count'])
                user_to_follow.save(update_fields=['follower_count'])
        except TransactionManagementError as e:
            return Response(json_response('error'),
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return Response(json_response('success',
                        'User follows ' + username + ' now.'),
                        status=status.HTTP_201_CREATED)

from django.contrib.auth.decorators import login_required
from django.db import DatabaseError, transaction
from django.shortcuts import redirect
from django.db.transaction import TransactionManagementError
from rest_framework.decorators import api_view
from rest_framework.request import Request
from rest_framework.response import Response
from xterver.lib.response import json_response
from rest_framework import status
from xterver.actions import (
    get_user_by_username, do_check_user_follows_user, do_create_connection,
    do_remove_connection, do_create_xtweet, get_user_xtweet, do_mark_xtweet_deleted
)
from xterver.models import UserXtweet

@login_required(login_url='/login')
def handle_xtweet_delete(request: Request, user_xtweet: UserXtweet) -> Response:
    if request.user != user_xtweet.user:
        return Response(json_response('error', 'Cannot delete xtweet from foreign profile.'),
                        status=status.HTTP_403_FORBIDDEN)
    try:
        xtweet_delete_status = do_mark_xtweet_deleted(user_xtweet.id)
    except DatabaseError:
        return Response(json_response('error'),
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    return Response(json_response('success',
                    data={
                    'msg': 'Xtweet Deleted.',
                    'tweet_id': user_xtweet.id}),
                    status=status.HTTP_200_OK)

@api_view(['GET', 'DELETE'])
def handle_xtweet_actions(request: Request, username: str, xtweet_id: int) -> Response:
    user_xtweet = get_user_xtweet(xtweet_id)
    if user_xtweet is None or user_xtweet.is_deleted:
        return Response(json_response('error', 'No such Xtweet found.'),
                        status=status.HTTP_404_NOT_FOUND)

    if request.method == 'DELETE':
        return handle_xtweet_delete(request, user_xtweet)

    # We can probably in future add support for tweet visibility over here by
    # performing checks relating to access of xtweets for a particular user.
    if user_xtweet.user.username != username:
        return redirect('/%s/xtweets/%d' % (user_xtweet.user.username, xtweet_id))
    return Response(json_response('success',
                    data={
                    'msg': '',
                    'username': username,
                    'tweet_id': xtweet_id,
                    'xtweet_content': user_xtweet.xtweet.content,
                    'xtweet_publish_datatime': user_xtweet.publish_datetime}),
                    status=status.HTTP_200_OK)

@login_required(login_url='/login')
@api_view(['POST'])
def handle_xtweet_creation(request: Request, username: str) -> Response:
    if request.method == 'POST':
        userxtweetsprofile = get_user_by_username(username)
        if userxtweetsprofile is None:
            return Response(json_response('error', 'Invalid username.'),
                            status=status.HTTP_404_NOT_FOUND)
        if request.user != userxtweetsprofile:
            return Response(json_response('error', 'Cannot xtweet from foreign profile.'),
                            status=status.HTTP_403_FORBIDDEN)
        data = request.data.get('data', None)
        if data is None:
            return Response(json_response('error', 'Missing data.'),
                            status=status.HTTP_400_BAD_REQUEST)
        xtweet_content = data.get('xtweet_content', None)
        if len(xtweet_content) > 140:
            return Response(json_response('error', 'xtweet too long. Max length acceptable 140 characters.'),
                            status=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE)
        try:
            new_user_xtweet = do_create_xtweet(userxtweetsprofile, xtweet_content)
        except TransactionManagementError as e:
            return Response(json_response('error'),
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response(json_response('success',
                        data={
                        'msg': 'Xtweet created',
                        'tweet_id': new_user_xtweet.id}),
                        status=status.HTTP_201_CREATED)

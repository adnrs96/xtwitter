from django.test import Client
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework.response import Response
from xterver.models import UserProfile, UserConfirmation
from xterver.actions import do_create_user

class UserFollowUnfollowTest(APITestCase):
    def setUp(self):
        full_name = 'Aditya Bansal'
        email = 'aditya@bansal.com'
        username = 'adnrs96'
        password = 'aditya@123'
        do_create_user(full_name=full_name,
                       email=email,
                       username=username,
                       password=password)
        full_name = 'Akshay Bist'
        email = 'akshay@bist.com'
        username = 'bakshay'
        password = 'akshay@123'
        do_create_user(full_name=full_name,
                       email=email,
                       username=username,
                       password=password)

    def test_follow_user(self):
        """
        Test we are able to follow user.
        This basically tests the /users/<slug: username>/follow endpoint.
        """
        url = '/users/tereesa/follow'
        c = Client()

        # Test not logged in requests are redirected to login page.
        response = c.put(url)
        self.assertEqual(response.status_code, status.HTTP_302_FOUND)
        self.assertIn(response.url, '/login?next=/users/tereesa/follow')

        c.login(username='adnrs96', password='aditya@123')

        # Test user to follow exits.
        response = c.put(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        url = '/users/adnrs96/follow'

        # Test you cannot follow yourself.
        response = c.put(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        url = '/users/bakshay/follow'
        # Test follow success
        response = c.put(url)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Test you cannot follow whom you already follow.
        response = c.put(url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_user_unfollow(self):
        """
        Test we are able to unfollow user.
        This basically tests the /users/<slug: username>/follow endpoint with a
        DELETE request.
        """
        url = '/users/tereesa/follow'
        c = Client()

        # Test not logged in requests are redirected to login page.
        response = c.delete(url)
        self.assertEqual(response.status_code, status.HTTP_302_FOUND)
        self.assertIn(response.url, '/login?next=/users/tereesa/follow')

        c.login(username='adnrs96', password='aditya@123')

        # Test user to follow exits.
        response = c.delete(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        # Test user unfollow success
        url = '/users/bakshay/follow'
        # Test follow success
        response = c.put(url)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        response = c.delete(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Test user unfollow whom you don't follow.
        response = c.delete(url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

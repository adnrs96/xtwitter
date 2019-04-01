from django.test import Client
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework.response import Response
from xterver.models import UserProfile, UserConfirmation
from xterver.actions import do_create_user

class AccountsTest(APITestCase):
    def setUp(self):
        full_name = 'Aditya Bansal'
        email = 'aditya@bansal.com'
        username = 'adnrs96'
        password = 'aditya@123'
        do_create_user(full_name=full_name,
                       email=email,
                       username=username,
                       password=password)

    def test_account_login(self):
        """
        Test we are able to login a user into his/her account.
        This basically tests the /login endpoint.
        """
        url = '/login'
        c = Client()

        # Test wrong email
        data = {'email': 'adnrs96', 'password': 'aditya@123'}
        response = c.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # Test wrong password
        data = {'email': 'adnrs96', 'password': 'aditya@1234'}
        response = c.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # Test login success
        data = {'email': 'aditya@bansal.com', 'password': 'aditya@123'}
        res_data = {'result': 'success', 'msg': 'Logged In'}
        response = c.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, res_data)

    def test_account_logout(self):
        """
        Test that we are able to logout user.
        It doesn't matter if user was logged in the first place.
        """
        url = '/logout'
        c = Client()

        response = c.delete(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

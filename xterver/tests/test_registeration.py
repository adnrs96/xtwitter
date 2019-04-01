from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework.response import Response
from xterver.models import UserProfile, UserConfirmation
from typing import Dict

class RegisterationTest(APITestCase):
    def test_new_registeration(self):
        """
        Test we are able to register a new user for confirmation of email.
        This basically tests the /accounts/new endpoint.
        """
        url = '/accounts/new'

        def test_failures(data: Dict[str, str]) -> Response:
            count_before = UserConfirmation.objects.all().count()
            response = self.client.post(url, data, format='json')
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            self.assertEqual(UserConfirmation.objects.all().count(), count_before)
            return response
        # Test missing full name.
        data = {'email': 'akshay'}
        test_failures(data)

        # Test missing email.
        data = {'full_name': 'Akshay Bist'}
        test_failures(data)

        # Test invalid email.
        data = {'email': 'akshay', 'full_name': 'Akshay Bist'}
        test_failures(data)

        # Test successful pre registeration.
        data = {'email': 'akshay@getpostman.com', 'full_name': 'Akshay Bist'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(UserConfirmation.objects.all().count(), 1)
        self.assertEqual(UserConfirmation.objects.all().first().email,
                         'akshay@getpostman.com')
        # Test duplicate email.
        data = {'email': 'akshay@getpostman.com', 'full_name': 'Akshay Bist'}
        test_failures(data)

    def test_confirm_registeration(self):
        """
        Test we are able to confirm a new user email id.
        This basically tests the /accounts/confirm endpoint.
        """
        url = '/accounts/confirm'

        data = {'email': 'akshay@getpostman.com', 'full_name': 'Akshay Bist'}
        response = self.client.post('/accounts/new', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        confirmation_key = UserConfirmation.objects.all().first().confirmation_key

        def test_failures(data: Dict[str, str], status: int=status.HTTP_400_BAD_REQUEST) -> Response:
            count_before = UserConfirmation.objects.all().count()
            response = self.client.post(url, data, format='json')
            self.assertEqual(response.status_code, status)
            self.assertEqual(UserConfirmation.objects.all().count(), count_before)
            return response

        # Test missing key.
        data = {'email': 'akshay'}
        test_failures(data)

        # Test missing email.
        data = {'key': confirmation_key}
        test_failures(data)

        # Test invalid email.
        data = {'email': 'akshay', 'key': confirmation_key}
        test_failures(data)

        # Test email not registered for confirmation.
        data = {'email': 'aditya@getpostman.com', 'key': confirmation_key}
        test_failures(data, status.HTTP_404_NOT_FOUND)

        # Test invalid confirmation key.
        data = {'email': 'akshay@getpostman.com', 'key': 'test-key'}
        test_failures(data, status.HTTP_401_UNAUTHORIZED)

        # Test successful confirmation of email id.
        data = {'email': 'akshay@getpostman.com', 'key': confirmation_key}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(UserConfirmation.objects.all().count(), 1)
        self.assertTrue(UserConfirmation.objects.all().first().is_confirmed)

        # Test already confirmed email.
        data = {'email': 'akshay@getpostman.com', 'key': confirmation_key}
        test_failures(data, status.HTTP_417_EXPECTATION_FAILED)

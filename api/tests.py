# api/tests.py

from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from .models import User

class UserRegistrationAPITest(APITestCase):

    def test_user_can_register_successfully(self):
        """
        Ensure a new user can be created via the API.
        """
        # The URL for the registration endpoint. 'reverse' is the correct
        # way to get a URL in Django, avoiding hardcoded paths.
        url = reverse('user-register') 
        
        # The data we will send in our POST request.
        data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'someStrongPassword123',
            'is_pro': False
        }

        # Use the test client to make a POST request.
        response = self.client.post(url, data, format='json')

        # --- Assertions ---
        # We check that the server responded with a 201 CREATED status.
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # We check that a user was actually created in the database.
        self.assertEqual(User.objects.count(), 1)
        
        # We check that the created user has the correct username.
        self.assertEqual(User.objects.get().username, 'testuser')
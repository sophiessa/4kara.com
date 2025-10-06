# api/tests.py

from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from .models import User, Job, Bid

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


class JobAPITest(APITestCase):

    def setUp(self):
        """Set up initial users and jobs for testing."""
        # Create a customer user
        self.customer_user = User.objects.create_user(
            username='customer', password='password123', is_pro=False
        )
        # Create a professional user
        self.pro_user = User.objects.create_user(
            username='professional', password='password123', is_pro=True
        )

        # Create some jobs
        Job.objects.create(customer=self.customer_user, title='Job 1', description='...')
        Job.objects.create(customer=self.customer_user, title='Job 2', description='...')
        
        # URL for the job list
        self.list_url = reverse('job-list')

    def test_unauthenticated_user_cannot_list_jobs(self):
        """Ensure unauthenticated users get a 401 Unauthorized."""
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_customer_user_cannot_list_jobs(self):
        """Ensure non-pro users get a 403 Forbidden."""
        # Force authentication for the customer user
        self.client.force_authenticate(user=self.customer_user)
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        
    def test_pro_user_can_list_jobs(self):
        """Ensure pro users can successfully list jobs."""
        # Force authentication for the pro user
        self.client.force_authenticate(user=self.pro_user)
        response = self.client.get(self.list_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Check that both jobs are returned
        self.assertEqual(len(response.data), 2)




class BidAPITest(APITestCase):

    def setUp(self):
        """Set up users and a job for bid testing."""
        self.customer_user = User.objects.create_user('customer', 'p', is_pro=False)
        self.pro_user = User.objects.create_user('professional', 'p', is_pro=True)
        self.job = Job.objects.create(customer=self.customer_user, title='Test Job')

    def test_pro_can_place_bid(self):
        """Ensure a professional user can place a bid on a job."""
        # The URL for bidding on the specific job created in setUp.
        url = reverse('bid-create', kwargs={'job_id': self.job.id})
        data = {'amount': '150.00', 'details': 'I can do this job next week.'}
        
        # Authenticate as the professional user.
        self.client.force_authenticate(user=self.pro_user)
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Bid.objects.count(), 1)
        self.assertEqual(Bid.objects.get().pro, self.pro_user)
        self.assertEqual(Bid.objects.get().job, self.job)

    def test_customer_cannot_place_bid(self):
        """Ensure a customer (non-pro) user cannot place a bid."""
        url = reverse('bid-create', kwargs={'job_id': self.job.id})
        data = {'amount': '150.00', 'details': 'I want to bid on this.'}
        
        # Authenticate as the customer user.
        self.client.force_authenticate(user=self.customer_user)
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Bid.objects.count(), 0)

    def test_cannot_bid_on_nonexistent_job(self):
        """Ensure bidding on a job that doesn't exist returns a 404."""
        # URL for a job ID that does not exist (e.g., 999).
        url = reverse('bid-create', kwargs={'job_id': 999})
        data = {'amount': '100.00', 'details': 'Test bid details'}

        self.client.force_authenticate(user=self.pro_user)
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

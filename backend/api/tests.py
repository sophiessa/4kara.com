from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from .models import User, ProProfile, Job, Bid, Message

class UserRegistrationAPITest(APITestCase):
    def test_user_can_register_successfully(self):
        """
        Ensure a new user can be created via the API.
        """
        url = reverse('user-register') 

        data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'someStrongPassword123',
            'is_pro': False
        }

        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(User.objects.get().username, 'testuser')


class JobAPITest(APITestCase):
    def setUp(self):
        """Set up initial users and jobs for testing."""
        self.customer_user = User.objects.create_user(
            username='customer', password='password123', is_pro=False
        )
        self.pro_user = User.objects.create_user(
            username='professional', password='password123', is_pro=True
        )
        
        Job.objects.create(customer=self.customer_user, title='Job 1', description='...')
        Job.objects.create(customer=self.customer_user, title='Job 2', description='...')
        
        self.list_url = reverse('job-list')

    def test_unauthenticated_user_cannot_list_jobs(self):
        """Ensure unauthenticated users get a 401 Unauthorized."""
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_customer_user_cannot_list_jobs(self):
        """Ensure non-pro users get a 403 Forbidden."""
        self.client.force_authenticate(user=self.customer_user)
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        
    def test_pro_user_can_list_jobs(self):
        """Ensure pro users can successfully list jobs."""
        self.client.force_authenticate(user=self.pro_user)
        response = self.client.get(self.list_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)




class BidAPITest(APITestCase):
    def setUp(self):
        """Set up users and a job for bid testing."""
        self.customer_user = User.objects.create_user('customer', 'p', is_pro=False)
        self.pro_user = User.objects.create_user('professional', 'p', is_pro=True)
        self.job = Job.objects.create(customer=self.customer_user, title='Test Job')

    def test_pro_can_place_bid(self):
        """Ensure a professional user can place a bid on a job."""
        url = reverse('bid-create', kwargs={'job_id': self.job.id})
        data = {'amount': '150.00', 'details': 'I can do this job next week.'}
        
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
        
        self.client.force_authenticate(user=self.customer_user)
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Bid.objects.count(), 0)

    def test_cannot_bid_on_nonexistent_job(self):
        """Ensure bidding on a job that doesn't exist returns a 404."""
        url = reverse('bid-create', kwargs={'job_id': 999})
        data = {'amount': '100.00', 'details': 'Test bid details'}

        self.client.force_authenticate(user=self.pro_user)
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

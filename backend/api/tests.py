import os
from unittest.mock import patch, ANY
from google.oauth2 import id_token as google_id_token
from google.auth.transport import requests as google_requests
from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from .models import User, ProProfile, Job, Bid, Message
from .permissions import IsProfessionalUser


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


class ProProfileAPITest(APITestCase):
    def setUp(self):
        """Set up users for profile testing."""
        self.customer_user = User.objects.create_user(username='customer', password='password123', email='customer@test.com', is_pro=False)
        self.pro_user = User.objects.create_user(username='professional', password='password123', email='pro@test.com', is_pro=True, full_name="Pro User One")
        self.my_profile_url = reverse('my-pro-profile')
        self.public_profile_url = reverse('public-pro-profile', kwargs={'user_id': self.pro_user.id})

    def test_pro_can_retrieve_own_profile(self):
        """Ensure a logged-in professional can retrieve their (potentially auto-created) profile."""
        self.client.force_authenticate(user=self.pro_user)
        response = self.client.get(self.my_profile_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['user'], self.pro_user.id)
        self.assertTrue(ProProfile.objects.filter(user=self.pro_user).exists())

    def test_pro_can_update_own_profile(self):
        """Ensure a logged-in professional can update their profile."""
        self.client.force_authenticate(user=self.pro_user)
        self.client.get(self.my_profile_url)
        update_data = {
            'bio': 'Experienced plumber specializing in leaks.',
            'service_area_zip_codes': '75201,75205',
            'profile_picture_url': 'http://example.com/image.jpg'
        }
        response = self.client.patch(self.my_profile_url, update_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'], 'Profile updated successfully.')
        self.assertEqual(response.data['data']['bio'], update_data['bio'])
        updated_profile = ProProfile.objects.get(user=self.pro_user)
        self.assertEqual(updated_profile.bio, update_data['bio'])
        self.assertEqual(updated_profile.service_area_zip_codes, update_data['service_area_zip_codes'])

    def test_customer_cannot_access_my_pro_profile_endpoint(self):
        """Ensure non-professionals get 403 Forbidden on the 'my-pro-profile' endpoint."""
        self.client.force_authenticate(user=self.customer_user)
        response = self.client.get(self.my_profile_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_unauthenticated_cannot_access_my_pro_profile_endpoint(self):
        """Ensure unauthenticated users get 401 Unauthorized."""
        response = self.client.get(self.my_profile_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_anyone_can_view_public_pro_profile(self):
        """Ensure anyone (even unauthenticated) can view a pro's public profile page."""
        ProProfile.objects.create(user=self.pro_user, bio="Test Bio")
        response = self.client.get(self.public_profile_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['bio'], "Test Bio")
        self.assertEqual(response.data['full_name'], "Pro User One")
        self.client.force_authenticate(user=self.customer_user)
        response = self.client.get(self.public_profile_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_view_nonexistent_public_profile_returns_404(self):
        """Ensure viewing a profile for a user ID that doesn't exist returns 404."""
        non_existent_url = reverse('public-pro-profile', kwargs={'user_id': 9999})
        response = self.client.get(non_existent_url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class JobAPITest(APITestCase):
    def setUp(self):
        """Set up initial users and jobs for testing."""
        self.customer_user = User.objects.create_user(username='customer', password='password123', is_pro=False)
        self.pro_user = User.objects.create_user(username='professional', password='password123', is_pro=True)
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


class MyJobsAPITest(APITestCase):
    def setUp(self):
        """Set up users and jobs."""
        self.customer1 = User.objects.create_user(username='cust1', password='p', email='c1@test.com', is_pro=False)
        self.customer2 = User.objects.create_user(username='cust2', password='p', email='c2@test.com', is_pro=False)
        self.pro_user = User.objects.create_user(username='pro', password='p', email='p@test.com', is_pro=True)
        Job.objects.create(customer=self.customer1, title='Job 1 by Cust1', description='...')
        Job.objects.create(customer=self.customer1, title='Job 2 by Cust1', description='...')
        Job.objects.create(customer=self.customer2, title='Job 1 by Cust2', description='...')
        self.my_jobs_url = reverse('my-jobs-list')

    def test_customer_can_list_own_jobs(self):
        """Ensure a logged-in customer sees only their jobs."""
        self.client.force_authenticate(user=self.customer1)
        response = self.client.get(self.my_jobs_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        job_titles = [job['title'] for job in response.data]
        self.assertIn('Job 1 by Cust1', job_titles)
        self.assertIn('Job 2 by Cust1', job_titles)
        self.assertNotIn('Job 1 by Cust2', job_titles)

    def test_another_customer_sees_only_their_jobs(self):
        """Ensure a different logged-in customer sees only their jobs."""
        self.client.force_authenticate(user=self.customer2)
        response = self.client.get(self.my_jobs_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['title'], 'Job 1 by Cust2')

    def test_pro_sees_no_jobs_on_my_jobs_endpoint(self):
        """Ensure a professional sees an empty list on the customer 'my-jobs' endpoint."""
        self.client.force_authenticate(user=self.pro_user)
        response = self.client.get(self.my_jobs_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)

    def test_unauthenticated_cannot_list_my_jobs(self):
        """Ensure unauthenticated users get 401 Unauthorized."""
        response = self.client.get(self.my_jobs_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class JobListFilteringSearchAPITest(APITestCase):
    def setUp(self):
        """Set up users and diverse jobs for filtering/searching."""
        self.customer = User.objects.create_user(username='cust_filter', password='p', email='cf@test.com', is_pro=False)
        self.pro_user = User.objects.create_user(username='pro_filter', password='p', email='pf@test.com', is_pro=True)
        self.non_pro_user = User.objects.create_user(username='nonpro_filter', password='p', email='npf@test.com', is_pro=False)
        Job.objects.create(
            customer=self.customer, title="Leaky Faucet Repair", description="Need a plumber for kitchen sink.",
            street_address="123 Main St", city="Dallas", state="TX", zip_code="75201"
        )
        Job.objects.create(
            customer=self.customer, title="Install Ceiling Fan", description="Electrician needed for bedroom fan.",
            street_address="456 Oak Ave", city="Dallas", state="TX", zip_code="75206"
        )
        Job.objects.create(
            customer=self.customer, title="Paint Living Room", description="Looking for a painter.",
            street_address="789 Pine Ln", city="Plano", state="TX", zip_code="75024"
        )
        Job.objects.create(
            customer=self.customer, title="Old Leaky Faucet Job", description="Plumber fixed this.",
            street_address="10 Downing St", city="London", state="UK", zip_code="SW1A", is_completed=True
        )
        self.jobs_url = reverse('job-list')

    def test_search_by_title_keyword(self):
        """Test searching jobs by a keyword in the title."""
        self.client.force_authenticate(user=self.pro_user)
        response = self.client.get(self.jobs_url, {'search': 'Faucet'})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['title'], 'Leaky Faucet Repair')

    def test_search_by_description_keyword(self):
        """Test searching jobs by a keyword in the description."""
        self.client.force_authenticate(user=self.pro_user)
        response = self.client.get(self.jobs_url, {'search': 'plumber'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['title'], 'Leaky Faucet Repair')

    def test_filter_by_zip_code(self):
        """Test filtering jobs by an exact zip code."""
        self.client.force_authenticate(user=self.pro_user)
        response = self.client.get(self.jobs_url, {'zip_code': '75206'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['title'], 'Install Ceiling Fan')

    def test_search_and_filter_combined(self):
        """Test combining search and zip code filter."""
        self.client.force_authenticate(user=self.pro_user)
        response = self.client.get(self.jobs_url, {'search': 'Repair', 'zip_code': '75201'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['title'], 'Leaky Faucet Repair')

    def test_search_no_results(self):
        """Test a search query that yields no results."""
        self.client.force_authenticate(user=self.pro_user)
        response = self.client.get(self.jobs_url, {'search': 'nonexistentkeyword'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)

    def test_non_pro_cannot_access_job_list(self):
        """Ensure non-professionals are blocked by IsProfessionalUser permission."""
        self.client.force_authenticate(user=self.non_pro_user)
        response = self.client.get(self.jobs_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class MyWorkAPITest(APITestCase):
    def setUp(self):
        """Set up users, jobs, bids, and accept one."""
        self.customer = User.objects.create_user(username='cust', password='p', email='c@test.com', is_pro=False)
        self.pro1 = User.objects.create_user(username='pro1', password='p', email='p1@test.com', is_pro=True)
        self.pro2 = User.objects.create_user(username='pro2', password='p', email='p2@test.com', is_pro=True)
        self.job1 = Job.objects.create(customer=self.customer, title='Job 1 for Pro1')
        self.bid1 = Bid.objects.create(job=self.job1, pro=self.pro1, amount=100)
        self.job1.accepted_bid = self.bid1
        self.job1.save()
        self.job2 = Job.objects.create(customer=self.customer, title='Job 2 for Pro2')
        self.bid2 = Bid.objects.create(job=self.job2, pro=self.pro2, amount=200)
        self.job2.accepted_bid = self.bid2
        self.job2.save()
        self.job3 = Job.objects.create(customer=self.customer, title='Job 3 Open')
        Bid.objects.create(job=self.job3, pro=self.pro1, amount=50)
        self.my_work_url = reverse('my-work-list')

    def test_hired_pro_can_list_accepted_jobs(self):
        """Ensure a logged-in pro sees only jobs where their bid was accepted."""
        self.client.force_authenticate(user=self.pro1)
        response = self.client.get(self.my_work_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['title'], 'Job 1 for Pro1')

    def test_another_hired_pro_sees_their_jobs(self):
        """Ensure a different hired pro sees only their accepted jobs."""
        self.client.force_authenticate(user=self.pro2)
        response = self.client.get(self.my_work_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['title'], 'Job 2 for Pro2')

    def test_customer_cannot_access_my_work(self):
        """Ensure a customer gets 403 Forbidden on the 'my-work' endpoint."""
        self.client.force_authenticate(user=self.customer)
        response = self.client.get(self.my_work_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_unauthenticated_cannot_access_my_work(self):
        """Ensure unauthenticated users get 401 Unauthorized."""
        response = self.client.get(self.my_work_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


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


class AcceptBidAPITest(APITestCase):
    def setUp(self):
        """Set up users, job, and a bid."""
        self.customer = User.objects.create_user(username='cust_accept', password='p', email='ca@test.com', is_pro=False)
        self.pro = User.objects.create_user(username='pro_accept', password='p', email='pa@test.com', is_pro=True)
        self.other_user = User.objects.create_user(username='other_accept', password='p', email='oa@test.com', is_pro=False)
        self.job = Job.objects.create(customer=self.customer, title='Job to Accept Bid', description='...')
        self.bid = Bid.objects.create(job=self.job, pro=self.pro, amount=150)
        self.accept_url = reverse('accept-bid', kwargs={'bid_id': self.bid.id})

    def test_customer_can_accept_bid(self):
        """Ensure the job owner can accept a valid bid."""
        self.client.force_authenticate(user=self.customer)
        response = self.client.post(self.accept_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('success', response.data)
        self.job.refresh_from_db()
        self.assertEqual(self.job.accepted_bid, self.bid)
        self.assertTrue(self.job.is_completed)

    def test_non_owner_cannot_accept_bid(self):
        """Ensure a user who doesn't own the job cannot accept a bid."""
        self.client.force_authenticate(user=self.other_user)
        response = self.client.post(self.accept_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.job.refresh_from_db()
        self.assertIsNone(self.job.accepted_bid)
        self.assertFalse(self.job.is_completed)

    def test_pro_cannot_accept_bid(self):
        """Ensure the professional who placed the bid cannot accept it."""
        self.client.force_authenticate(user=self.pro)
        response = self.client.post(self.accept_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.job.refresh_from_db()
        self.assertIsNone(self.job.accepted_bid)

    def test_cannot_accept_nonexistent_bid(self):
        """Ensure accepting a bid that doesn't exist returns 404."""
        non_existent_url = reverse('accept-bid', kwargs={'bid_id': 9999})
        self.client.force_authenticate(user=self.customer)
        response = self.client.post(non_existent_url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_cannot_accept_bid_on_already_completed_job(self):
        """Test attempting to accept a bid when one is already accepted."""
        self.client.force_authenticate(user=self.customer)
        self.client.post(self.accept_url)
        self.job.refresh_from_db()
        self.assertTrue(self.job.is_completed)
        another_bid = Bid.objects.create(job=self.job, pro=self.pro, amount=160)
        another_accept_url = reverse('accept-bid', kwargs={'bid_id': another_bid.id})
        response = self.client.post(another_accept_url)
        self.job.refresh_from_db()
        self.assertTrue(self.job.is_completed) 


class MessageAPITest(APITestCase):
    def setUp(self):
        """Set up users, a job with an accepted bid."""
        self.customer = User.objects.create_user(username='customer', password='p', email='cust@test.com', is_pro=False)
        self.pro = User.objects.create_user(username='hiredpro', password='p', email='hired@test.com', is_pro=True)
        self.other_pro = User.objects.create_user(username='otherpro', password='p', email='other@test.com', is_pro=True)
        self.job = Job.objects.create(customer=self.customer, title='Test Job for Messaging')
        self.bid = Bid.objects.create(job=self.job, pro=self.pro, amount=100)
        self.job.accepted_bid = self.bid
        self.job.is_completed = True
        self.job.save()
        Message.objects.create(job=self.job, sender=self.customer, receiver=self.pro, body="Hello Pro!")
        Message.objects.create(job=self.job, sender=self.pro, receiver=self.customer, body="Hello Customer!")

        self.list_url = reverse('message-list', kwargs={'job_id': self.job.id})
        self.create_url = reverse('message-create', kwargs={'job_id': self.job.id})

    def test_customer_can_list_messages(self):
        """Ensure the job customer can list messages for their job."""
        self.client.force_authenticate(user=self.customer)
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_hired_pro_can_list_messages(self):
        """Ensure the hired professional can list messages for the job."""
        self.client.force_authenticate(user=self.pro)
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_other_user_cannot_list_messages(self):
        """Ensure an unrelated user cannot list messages."""
        self.client.force_authenticate(user=self.other_pro)
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)

    def test_unauthenticated_cannot_list_messages(self):
        """Ensure unauthenticated users cannot list messages."""
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_customer_can_create_message(self):
        """Ensure the customer can send a message."""
        self.client.force_authenticate(user=self.customer)
        message_data = {'body': 'New message from customer.'}
        response = self.client.post(self.create_url, message_data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Message.objects.count(), 3)
        new_message = Message.objects.latest('timestamp')
        self.assertEqual(new_message.sender, self.customer)
        self.assertEqual(new_message.receiver, self.pro)
        self.assertEqual(new_message.body, message_data['body'])

    def test_hired_pro_can_create_message(self):
        """Ensure the hired pro can send a message."""
        self.client.force_authenticate(user=self.pro)
        message_data = {'body': 'New message from pro.'}
        response = self.client.post(self.create_url, message_data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Message.objects.count(), 3)
        new_message = Message.objects.latest('timestamp')
        self.assertEqual(new_message.sender, self.pro)
        self.assertEqual(new_message.receiver, self.customer)
        self.assertEqual(new_message.body, message_data['body'])

    def test_other_user_cannot_create_message(self):
        """Ensure an unrelated user cannot send a message."""
        self.client.force_authenticate(user=self.other_pro)
        message_data = {'body': 'Trying to interfere.'}
        response = self.client.post(self.create_url, message_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Message.objects.count(), 2)

    def test_unauthenticated_cannot_create_message(self):
        """Ensure unauthenticated users cannot send messages."""
        message_data = {'body': 'Anonymous message.'}
        response = self.client.post(self.create_url, message_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class GoogleLoginAPITest(APITestCase):
    def setUp(self):
        """Set up URL for Google login endpoint."""
        self.google_login_url = reverse('google-login')

    @patch('google.oauth2.id_token.verify_oauth2_token')
    def test_google_login_new_user(self, mock_verify_oauth2_token):
        """Test Google login creating a new user."""
        mock_google_user_info = {
            'iss': 'https://accounts.google.com',
            'azp': 'YOUR_GOOGLE_CLIENT_ID',
            'aud': 'YOUR_GOOGLE_CLIENT_ID',
            'sub': '12345678901234567890',
            'email': 'newuser@gmail.com',
            'email_verified': True,
            'name': 'New Google User',
            'picture': 'http://example.com/pic.jpg',
            'given_name': 'New',
            'family_name': 'User',
            'locale': 'en',
            'iat': 1600000000,
            'exp': 1600003600,
        }
        mock_verify_oauth2_token.return_value = mock_google_user_info
        request_data = {'id_token': 'fake_google_id_token_string'}
        response = self.client.post(self.google_login_url, request_data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('key', response.data)
        self.assertIn('user', response.data)
        self.assertEqual(response.data['user']['email'], 'newuser@gmail.com')
        self.assertEqual(response.data['user']['full_name'], 'New Google User')
        self.assertTrue(User.objects.filter(email='newuser@gmail.com').exists())
        new_user = User.objects.get(email='newuser@gmail.com')
        self.assertEqual(new_user.full_name, 'New Google User')


        mock_verify_oauth2_token.assert_called_once_with(
            request_data['id_token'],
            ANY,
            os.environ.get('GOOGLE_OAUTH_CLIENT_ID')
        )

    @patch('google.oauth2.id_token.verify_oauth2_token')
    def test_google_login_existing_user(self, mock_verify_oauth2_token):
        """Test Google login for an existing user created via Google."""
        existing_email = 'existing@gmail.com'
        User.objects.create_user(email=existing_email, username=existing_email, full_name="Existing User")
        initial_user_count = User.objects.count()
        mock_google_user_info = {
            'email': existing_email,
            'name': 'Existing User',
            'iss': 'https://accounts.google.com', 'aud': os.environ.get('GOOGLE_OAUTH_CLIENT_ID'), 'sub': '98765'
        }
        mock_verify_oauth2_token.return_value = mock_google_user_info
        request_data = {'id_token': 'another_fake_token'}
        response = self.client.post(self.google_login_url, request_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('key', response.data)
        self.assertEqual(response.data['user']['email'], existing_email)
        self.assertEqual(User.objects.count(), initial_user_count)

    @patch('google.oauth2.id_token.verify_oauth2_token')
    def test_google_login_invalid_token(self, mock_verify_oauth2_token):
        """Test Google login fails with an invalid token."""
        mock_verify_oauth2_token.side_effect = ValueError("Invalid token")
        request_data = {'id_token': 'invalid_token_string'}
        response = self.client.post(self.google_login_url, request_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
        self.assertEqual(response.data['error'], 'Invalid Google token')

    def test_google_login_missing_token(self):
        """Test Google login fails if no token is provided."""
        response = self.client.post(self.google_login_url, {}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
        self.assertEqual(response.data['error'], 'ID token is required')
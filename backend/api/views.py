import os
from google.oauth2 import id_token as google_id_token
from google.auth.transport import requests as google_requests
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.permissions import AllowAny

from django.shortcuts import get_object_or_404
from rest_framework import generics, permissions
from .models import User, Job, Bid, Message
from .serializers import UserSerializer, JobSerializer, BidSerializer, MessageSerializer
from rest_framework.permissions import IsAuthenticated, AllowAny
from .permissions import IsProfessionalUser
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
from rest_framework import status
from rest_framework import generics, permissions
from rest_framework.filters import SearchFilter, OrderingFilter 
from django_filters.rest_framework import DjangoFilterBackend


class UserCreateView(generics.CreateAPIView):
    """
    A view for creating new users.
    `CreateAPIView` is a generic view provided by DRF that handles POST requests for creating objects.
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AllowAny]
    authentication_classes = []
    


class JobCreateView(generics.CreateAPIView):
    queryset = Job.objects.all()
    serializer_class = JobSerializer
    # This ensures only authenticated (logged-in) users can access this endpoint.
    permission_classes = [IsAuthenticated]


    def perform_create(self, serializer):
        # When a new job is created, this method is called.
        # We automatically set the job's 'customer' to the currently logged-in user.
        serializer.save(customer=self.request.user)


    

class JobListView(generics.ListAPIView):
    """
    A view for professionals to list all available (incomplete) jobs,
    with search, filtering, and ordering capabilities.
    """
    serializer_class = JobSerializer
    permission_classes = [IsProfessionalUser]
    

    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['zip_code', 'state'] # Allow filtering by these exact fields
    search_fields = ['title', 'description'] # Allow full-text search on these fields
    ordering_fields = ['created_at', 'city'] # Allow sorting by these fields


    def get_queryset(self):
        """
        This view should return a list of all jobs that are not yet completed.
        """
        return Job.objects.filter(is_completed=False)



class BidCreateView(generics.CreateAPIView):
    """
    A view for professionals to create a bid on a specific job.
    """
    serializer_class = BidSerializer
    permission_classes = [IsProfessionalUser] # Only pros can bid.

    def perform_create(self, serializer):
        """
        Associate the bid with the job from the URL and the user from the request.
        """
        # Get the job_id from the URL's keyword arguments.
        job_id = self.kwargs['job_id']
        # Use get_object_or_404 to fetch the job, which handles the "not found" case.
        job = get_object_or_404(Job, id=job_id)

        # You might add logic here to prevent bidding on your own job, for example.
        
        # Save the bid, associating it with the job and the authenticated pro user.
        serializer.save(job=job, pro=self.request.user)


class LoginView(APIView):
    """
    Custom login view to return user data along with the token.
    """
    # This view should be public.
    permission_classes = [permissions.AllowAny]
    authentication_classes = []

    def post(self, request, *args, **kwargs):
        username = request.data.get("username")
        password = request.data.get("password")
        user = authenticate(username=username, password=password)
        if user is not None:
            # User is valid, get or create a token.
            token, created = Token.objects.get_or_create(user=user)
            # Serialize the user data you want to return.
            user_data = {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "is_pro": user.is_pro,
                "full_name": user.full_name
            }
            return Response({"token": token.key, "user": user_data})
        else:
            # Invalid credentials.
            return Response({"error": "Invalid Credentials"}, status=400)


class JobDetailView(generics.RetrieveAPIView):
    """
    A view to retrieve a single job instance.
    """
    queryset = Job.objects.all()
    serializer_class = JobSerializer
    # Anyone who is logged in can view the details of a job.
    permission_classes = [IsAuthenticated]


class AcceptBidView(APIView):
    """
    A view for a customer to accept a bid on their job.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, bid_id, *args, **kwargs):
        # Get the bid object, or return 404 if it doesn't exist
        bid = get_object_or_404(Bid, id=bid_id)
        job = bid.job

        # Security Check: Ensure the user making the request owns the job.
        if job.customer != request.user:
            return Response(
                {"error": "You do not have permission to accept this bid."}, 
                status=status.HTTP_403_FORBIDDEN
            )

        # Update the job to accept the bid
        job.accepted_bid = bid
        job.is_completed = True # Mark the job as completed/closed for bidding
        job.save()

        return Response(
            {"success": f"Bid {bid.id} has been accepted for job '{job.title}'."},
            status=status.HTTP_200_OK
        )

class MyJobsListView(generics.ListAPIView):
    """
    A view for a customer to list only the jobs they have created.
    """
    serializer_class = JobSerializer
    permission_classes = [IsAuthenticated] # Must be logged in

    def get_queryset(self):
        """
        This view returns a list of all jobs created by the currently
        authenticated user.
        """
        user = self.request.user
        # We filter the Job objects to only those where the customer is the current user.
        return Job.objects.filter(customer=user).order_by('-created_at')


# Replace your old GoogleLoginView with this one
class GoogleLoginView(APIView):
    """
    Custom view for Google OAuth login.
    Receives an ID token from the frontend, verifies it with Google,
    and then creates or logs in the user, returning a DRF token.
    """
    permission_classes = [AllowAny]
    authentication_classes = []

    def post(self, request, *args, **kwargs):
        token = request.data.get('id_token')
        
        if not token:
            return Response({'error': 'ID token is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # 1. VERIFY THE TOKEN
            # This line sends the token to Google's servers to check if it's valid.
            # It also checks that the token was issued for YOUR application.
            idinfo = google_id_token.verify_oauth2_token(
                token, 
                google_requests.Request(), 
                os.environ.get('GOOGLE_OAUTH_CLIENT_ID')
            )

            print(os.environ.get('GOOGLE_OAUTH_CLIENT_ID'))
            
            # 2. GET USER INFO FROM VERIFIED TOKEN
            # If verify_oauth2_token doesn't raise an error, the token is valid.
            # We can now safely trust the information in idinfo.
            email = idinfo['email']
            full_name = idinfo.get('name', '')
            
            # 3. CREATE OR GET USER
            # Now we find the user with that verified email or create them.
            user, created = User.objects.get_or_create(
                email=email,
                defaults={
                    'username': email, # Use email as username for simplicity
                    'full_name': full_name,
                    'is_pro': False # Default new users to customer
                }
            )
            
            # 4. ISSUE YOUR APP'S TOKEN
            drf_token, created = Token.objects.get_or_create(user=user)
            
            # Prepare user data to send back to the frontend
            user_data = {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "is_pro": user.is_pro,
                "full_name": user.full_name
            }
            
            return Response({
                'key': drf_token.key,
                'user': user_data
            })
            
        except ValueError as e:
            # This error is raised if the token is invalid
            return Response({'error': 'Invalid Google token', 'details': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': 'An unexpected error occurred', 'details': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class MessageListView(generics.ListAPIView):
    """
    Lists messages for a specific job.
    Access is restricted to the job's customer and the accepted professional.
    """
    serializer_class = MessageSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        job_id = self.kwargs['job_id']
        job = get_object_or_404(Job, id=job_id)
        user = self.request.user

        # Security check: Ensure the user is either the customer or the hired pro.
        # The job must have an accepted bid to have a conversation.
        if job.accepted_bid and (user == job.customer or user == job.accepted_bid.pro):
            return Message.objects.filter(job=job).order_by('timestamp')
        
        # If the user is not a participant, return an empty list.
        return Message.objects.none()

class MessageCreateView(generics.CreateAPIView):
    """
    Creates a new message for a specific job.
    """
    serializer_class = MessageSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        job_id = self.kwargs['job_id']
        job = get_object_or_404(Job, id=job_id)
        user = self.request.user

        # Determine the receiver of the message.
        if user == job.customer:
            receiver = job.accepted_bid.pro
        elif job.accepted_bid and user == job.accepted_bid.pro:
            receiver = job.customer
        else:
            # If the user is not a participant, block the message creation.
            raise serializers.ValidationError("You do not have permission to post messages for this job.")

        serializer.save(job=job, sender=user, receiver=receiver)
import os
from .models import User, ProProfile, Job, Bid, Message
from .serializers import ProProfileSerializer, JobSerializer, BidSerializer, MessageSerializer
from .permissions import IsProfessionalUser

import vertexai
from vertexai.generative_models import GenerativeModel, Part, Content
from google.oauth2 import id_token as google_id_token
from google.auth.transport import requests as google_requests

from rest_framework import status, generics, serializers
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.filters import SearchFilter, OrderingFilter

from django.contrib.auth import authenticate
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404
from dotenv import load_dotenv

load_dotenv()


try:
    PROJECT_ID = os.environ.get('PROJECT_ID')
    LOCATION = os.environ.get('LOCATION')
    vertexai.init(project=PROJECT_ID, location=LOCATION)
except Exception as e:
    print(f'Error initializing Vertex AI: {e}')
    

class MyProProfileView(generics.RetrieveUpdateAPIView):
    """
    Allows a professional user to retrieve and update their own profile.
    get: Retrieve your profile.
    put: Update your profile.
    patch: Partially update your profile.
    """
    serializer_class = ProProfileSerializer
    permission_classes = [IsProfessionalUser]

    def get_object(self):
        profile, created = ProProfile.objects.get_or_create(user=self.request.user)
        return profile

    def update(self, request, *args, **kwargs):
        response = super().update(request, *args, **kwargs)
        if response.status_code == status.HTTP_200_OK:
            return Response({"message": "Profile updated successfully.", "data": response.data})
        return response


class PublicProProfileView(generics.RetrieveAPIView):
    """
    Allows anyone to view a specific professional's profile.
    get: Retrieve profile by user ID.
    """
    serializer_class = ProProfileSerializer
    permission_classes = [AllowAny]
    queryset = ProProfile.objects.all()
    lookup_field = 'user_id'


class JobCreateView(generics.CreateAPIView):
    """
    A view for customers to create new jobs.
    """
    queryset = Job.objects.all()
    serializer_class = JobSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(customer=self.request.user)


class JobListView(generics.ListAPIView):
    """
    A view for professionals to list all available (incomplete) jobs,
    with search, filtering, and ordering capabilities.
    """
    serializer_class = JobSerializer
    permission_classes = [IsProfessionalUser]

    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['zip_code', 'state']
    search_fields = ['title', 'description'] 
    ordering_fields = ['created_at', 'city']


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
    permission_classes = [IsProfessionalUser]

    def perform_create(self, serializer):
        """
        Associate the bid with the job from the URL and the user from the request.
        """
        job_id = self.kwargs['job_id']
        job = get_object_or_404(Job, id=job_id)
        serializer.save(job=job, pro=self.request.user)


class JobDetailView(generics.RetrieveAPIView):
    """
    A view to retrieve a single job instance.
    """
    queryset = Job.objects.all()
    serializer_class = JobSerializer
    permission_classes = [IsAuthenticated]


class AcceptBidView(APIView):
    """
    A view for a customer to accept a bid on their job.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, bid_id, *args, **kwargs):
        bid = get_object_or_404(Bid, id=bid_id)
        job = bid.job

        if job.customer != request.user:
            return Response(
                {"error": "You do not have permission to accept this bid."}, 
                status=status.HTTP_403_FORBIDDEN
            )

        job.accepted_bid = bid
        job.is_completed = True
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
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        This view returns a list of all jobs created by the currently
        authenticated user.
        """
        user = self.request.user
        return Job.objects.filter(customer=user).order_by('-created_at')


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
            idinfo = google_id_token.verify_oauth2_token(
                token, 
                google_requests.Request(), 
                os.environ.get('GOOGLE_OAUTH_CLIENT_ID')
            )

            print(os.environ.get('GOOGLE_OAUTH_CLIENT_ID'))
            
            email = idinfo['email']
            first_name = idinfo.get('given_name', '')
            last_name = idinfo.get('family_name', '')
            
            user, created = User.objects.get_or_create(
                email=email,
                defaults={
                    'username': email,
                    'first_name': first_name,
                    'last_name': last_name,
                    'is_pro': False
                }
            )
            
            drf_token, created = Token.objects.get_or_create(user=user)
            
            user_data = {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "is_pro": user.is_pro,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "phone_number": user.phone_number
            }
            
            return Response({
                'key': drf_token.key,
                'user': user_data
            })
            
        except ValueError as e:
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

        if job.accepted_bid and (user == job.customer or user == job.accepted_bid.pro):
            return Message.objects.filter(job=job).order_by('timestamp')

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

        if user == job.customer:
            receiver = job.accepted_bid.pro
        elif job.accepted_bid and user == job.accepted_bid.pro:
            receiver = job.customer
        else:
            raise serializers.ValidationError("You do not have permission to post messages for this job.")

        serializer.save(job=job, sender=user, receiver=receiver)


class MyAcceptedJobsListView(generics.ListAPIView):
    """
    A view for a professional to list the jobs they have been hired for.
    """
    serializer_class = JobSerializer
    permission_classes = [IsProfessionalUser]

    def get_queryset(self):
        """
        This view returns a list of all jobs where the currently
        authenticated user is the pro associated with the accepted bid.
        """
        user = self.request.user
        return Job.objects.filter(accepted_bid__pro=user).order_by('-created_at')
    

class ChatView(APIView):
    """
    Handles chat requests by sending prompts to the Vertex AI Gemini API.
    """
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        user_message = request.data.get('message')

        history_raw = request.data.get('history', [])
        if not user_message:
            return Response({'error': 'Message is required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            model = GenerativeModel("gemini-2.5-flash")

            gemini_history = []
            for msg in history_raw:
                role = "user" if msg.get("sender") == "user" else "model"
                part = Part.from_text(msg.get("text", ""))
                content = Content(parts=[part], role=role)
                gemini_history.append(content)

            system_instruction = f"""
            You are "ARA", ARA stands for Appliance Repair Assistant, a helpful AI assistant for 4kara.com, specializing in appliance repair and maintenance advice. Be friendly, empathetic, and knowledgeable.

            Help the user understand their appliance issue. Provide potential causes, simple DIY steps (if safe and appropriate), or suggest the type of professional they should hire through 4kara.com. 

            - DO NOT engage in conversations outside of Appliance Repair scope
            - DO NOT provide price estimates or quotes.
            - DO NOT recommend specific brands or companies.
            - DO NOT give advice that requires specialized tools or licenses (e.g., major electrical work, gas line repairs). Emphasize safety.
            - If asked for quotes or specific pros, politely explain you cannot provide that and suggest they "post a job on 4kara.com to get bids from qualified local professionals."
            - KEEP RESPONSES LESS THAN 30 WORDS
            """

            chat = model.start_chat(history=gemini_history)

            effective_message = user_message
            if not gemini_history:
                 effective_message = "\n\nUser message: \"" + user_message + "\"\nAssistant response: \n" + system_instruction

            response = chat.send_message(effective_message)

            ai_response = response.text
            return Response({'reply': ai_response})

        except Exception as e:
            print(f"Error calling Vertex AI: {e}")
            return Response({'error': 'Sorry, I encountered an error. Please try again.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
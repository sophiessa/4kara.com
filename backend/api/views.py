from django.shortcuts import get_object_or_404
from rest_framework import generics, permissions
from .models import User, Job, Bid
from .serializers import UserSerializer, JobSerializer, BidSerializer
from rest_framework.permissions import IsAuthenticated, AllowAny
from .permissions import IsProfessionalUser
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
from rest_framework import status


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
    A view for professionals to list all available (incomplete) jobs.
    """
    serializer_class = JobSerializer
    # This view is protected by our custom permission.
    permission_classes = [IsProfessionalUser]

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

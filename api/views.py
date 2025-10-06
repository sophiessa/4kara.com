from django.shortcuts import get_object_or_404
from rest_framework import generics, permissions
from .models import User, Job, Bid
from .serializers import UserSerializer, JobSerializer, BidSerializer
from rest_framework.permissions import IsAuthenticated, AllowAny
from .permissions import IsProfessionalUser

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

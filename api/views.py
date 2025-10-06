from rest_framework import generics, permissions
from .models import User, Job
from .serializers import UserSerializer, JobSerializer
from rest_framework.permissions import IsAuthenticated, AllowAny

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

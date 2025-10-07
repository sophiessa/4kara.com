from django.urls import path
from .views import UserCreateView, JobCreateView, JobListView, BidCreateView, LoginView, JobDetailView
from rest_framework.authtoken.views import obtain_auth_token

urlpatterns = [
    path('users/register/', UserCreateView.as_view(), name='user-register'),
    path('users/login/', LoginView.as_view(), name='user-login'),
    path('jobs/create/', JobCreateView.as_view(), name='job-create'),
    path('jobs/', JobListView.as_view(), name='job-list'),
    path('jobs/<int:job_id>/bid/', BidCreateView.as_view(), name='bid-create'),
    path('jobs/<int:pk>/', JobDetailView.as_view(), name='job-detail'),

]
from django.urls import path
from .views import (
    UserCreateView, JobCreateView, JobListView, 
    BidCreateView, LoginView, JobDetailView, 
    AcceptBidView, MyJobsListView, GoogleLoginView, 
    MessageCreateView, MessageListView, MyAcceptedJobsListView,
    ChatView,
    )
from rest_framework.authtoken.views import obtain_auth_token

urlpatterns = [
    path('users/register/', UserCreateView.as_view(), name='user-register'),
    path('users/login/', LoginView.as_view(), name='user-login'),
    path('jobs/create/', JobCreateView.as_view(), name='job-create'),
    path('jobs/', JobListView.as_view(), name='job-list'),
    path('jobs/<int:job_id>/bid/', BidCreateView.as_view(), name='bid-create'),
    path('jobs/<int:pk>/', JobDetailView.as_view(), name='job-detail'),
    path('bids/<int:bid_id>/accept/', AcceptBidView.as_view(), name='accept-bid'),
    path('my-jobs/', MyJobsListView.as_view(), name='my-jobs-list'),
    path('my-work/', MyAcceptedJobsListView.as_view(), name='my-work-list'),

    path('jobs/<int:job_id>/messages/', MessageListView.as_view(), name='message-list'),
    path('jobs/<int:job_id>/messages/create/', MessageCreateView.as_view(), name='message-create'),

    path('google/', GoogleLoginView.as_view(), name='google-login'),

    path('chat/', ChatView.as_view(), name='chat'),
]
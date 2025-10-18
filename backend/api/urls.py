from django.urls import path
from .views import (
    UserCreateView, JobCreateView, JobListView, 
    BidCreateView, LoginView, JobDetailView, 
    AcceptBidView, MyJobsListView, GoogleLoginView, 
    MessageCreateView, MessageListView, MyAcceptedJobsListView,
    ChatView, MyProProfileView, PublicProProfileView
    )
from rest_framework.authtoken.views import obtain_auth_token

urlpatterns = [
    path('users/register/', UserCreateView.as_view(), name='user-register'),
    path('users/login/', LoginView.as_view(), name='user-login'),
    path('google/', GoogleLoginView.as_view(), name='google-login'),
    
    path('jobs/', JobListView.as_view(), name='job-list'),
    path('jobs/create/', JobCreateView.as_view(), name='job-create'),
    path('jobs/<int:pk>/', JobDetailView.as_view(), name='job-detail'),
    path('jobs/<int:job_id>/bid/', BidCreateView.as_view(), name='bid-create'),
    path('bids/<int:bid_id>/accept/', AcceptBidView.as_view(), name='accept-bid'),
    path('jobs/<int:job_id>/messages/', MessageListView.as_view(), name='message-list'),
    path('jobs/<int:job_id>/messages/create/', MessageCreateView.as_view(), name='message-create'),
    path('my-jobs/', MyJobsListView.as_view(), name='my-jobs-list'),
    path('my-work/', MyAcceptedJobsListView.as_view(), name='my-work-list'),

    path('chat/', ChatView.as_view(), name='chat'),

    path('profile/pro/', MyProProfileView.as_view(), name='my-pro-profile'),    
    path('profiles/pro/<int:user_id>/', PublicProProfileView.as_view(), name='public-pro-profile'),
    
]
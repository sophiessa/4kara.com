# backend/fourkara/urls.py

from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    # 1. The Admin site
    path('admin/', admin.site.urls),

    # 2. Endpoints for dj-rest-auth (MUST include both)
    path('dj-rest-auth/', include('dj_rest_auth.urls')),
    path('dj-rest-auth/registration/', include('dj_rest_auth.registration.urls')),

    # 3. Your custom API endpoints (for jobs, bids, etc.)
    # This was the part that was likely broken or missing.
    path('api/', include('api.urls')),

    path('accounts/', include('allauth.urls')),
]
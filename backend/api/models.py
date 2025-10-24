from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings


class User(AbstractUser):
    """
    Custom User Model
    This model stores information for all users.
    The `is_pro` boolean field distinguishes between Customers and Professionals.
    """
    is_pro = models.BooleanField('Is professional', default=False)
    phone_number = models.CharField(max_length=20, blank=True)
    

class ProProfile(models.Model):
    """
    Stores additional information for a professional user.
    """
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='pro_profile' 
    )
    bio = models.TextField(blank=True)
    service_area_zip_codes = models.CharField(
        max_length=255,
        blank=True,
        help_text="Comma-separated list of zip codes served (e.g., 75201,75205)"
    )
    profile_picture_url = models.URLField(blank=True)

    years_experience = models.PositiveIntegerField(null=True, blank=True)
    instagram_url = models.URLField(blank=True, help_text="Link to Instagram profile (optional)")
    facebook_url = models.URLField(blank=True, help_text="Link to Facebook profile (optional)")
    twitter_url = models.URLField(blank=True, help_text="Link to Twitter profile (optional)")
    personal_website_url = models.URLField(blank=True, help_text="Link to personal website (optional)")
    services_offered = models.TextField(blank=True, help_text="Describe the main services you provide.")
    availability = models.CharField(max_length=255, blank=True, help_text="e.g., Weekdays 9am-5pm, Emergency calls available")
    faq = models.TextField(blank=True, help_text="Optional FAQ section (e.g., Q: What's your hourly rate? A: ...)")

    def __str__(self):
        return f"{self.user.username}'s Pro Profile" 


class Job(models.Model):
    """
    Job Model
    This model stores all the job requests posted by customers.
    """
    customer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='jobs')
    title = models.CharField(max_length=255)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_completed = models.BooleanField(default=False)

    street_address = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=50)
    zip_code = models.CharField(max_length=10)
    
    accepted_bid = models.ForeignKey(
        'Bid', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='accepted_for_job'
    )

    def __str__(self):
        return self.title


class Bid(models.Model):
    """
    Bid Model
    This model stores the bids made by Professionals on a Job.
    """
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='bids')
    pro = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bids')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    details = models.TextField(help_text="Details about the bid, like scope of work.")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Bid of ${self.amount} by {self.pro.username} on '{self.job.title}'"


class Message(models.Model):
    """
    A model for a single message in a conversation.
    """
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_messages')
    body = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'From {self.sender.username} to {self.receiver.username} re: "{self.job.title}"'
    

class Review(models.Model):
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='reviews')
    pro = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews_received', limit_choices_to={'is_pro': True})
    customer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews_written', limit_choices_to={'is_pro': False})
    rating = models.PositiveSmallIntegerField(choices=[(1, '1'), (2, '2'), (3, '3'), (4, '4'), (5, '5')])
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('job', 'pro', 'customer')

    def __str__(self):
        return f'Review by {self.customer.username} for {self.pro.username} on job {self.job.id} ({self.rating} stars)'
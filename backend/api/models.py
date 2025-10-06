from django.db import models
from django.contrib.auth.models import AbstractUser

# We are extending Django's built-in User model to add a user type.
class User(AbstractUser):
    """
    Custom User Model
    This model stores information for all users.
    The `is_pro` boolean field distinguishes between Customers and Professionals.
    """
    is_pro = models.BooleanField('Is professional', default=False)

class Job(models.Model):
    """
    Job Model
    This model stores all the job requests posted by customers.
    """
    # The customer who posted the job. It's linked to our User model.
    # If a user is deleted, all their jobs will be deleted too (CASCADE).
    customer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='jobs')
    title = models.CharField(max_length=255)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_completed = models.BooleanField(default=False)

    def __str__(self):
        return self.title

class Bid(models.Model):
    """
    Bid Model
    This model stores the bids made by Professionals on a Job.
    """
    # The job the bid is for.
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='bids')
    # The professional who made the bid.
    pro = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bids')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    details = models.TextField(help_text="Details about the bid, like scope of work.")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Bid of ${self.amount} by {self.pro.username} on '{self.job.title}'"
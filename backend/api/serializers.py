from rest_framework import serializers
from .models import User, Job, Bid

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        # These are the fields that will be sent to the client and received from the client.
        fields = ('id', 'username', 'email', 'password', 'is_pro')
        # We add extra settings for the password field.
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        """
        This method is called when a new user is created.
        We handle the password hashing here.
        """
        password = validated_data.pop('password', None)
        instance = self.Meta.model(**validated_data)
        if password is not None:
            # This is the correct way to set a password in Django, it handles hashing.
            instance.set_password(password)
        instance.save()
        return instance

class BidSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bid
        # The user will only submit the amount and details.
        fields = ['id', 'job', 'pro', 'amount', 'details', 'created_at']
        # The job and pro will be set by the view, so they are read-only here.
        read_only_fields = ['job', 'pro']

class JobSerializer(serializers.ModelSerializer):
    # Add this line to include the bids in the serializer.
    bids = BidSerializer(many=True, read_only=True)
    class Meta:
        model = Job
        # We only need title and description from the user when creating a job.
        # The 'customer' will be set automatically from the logged-in user.
        fields = ['id', 'title', 'description', 'customer', 'created_at', 'is_completed', 'bids']
        # Make the customer field read-only in the serializer.
        read_only_fields = ['customer']


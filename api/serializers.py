from rest_framework import serializers
from .models import User, Job

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

class JobSerializer(serializers.ModelSerializer):
    class Meta:
        model = Job
        # We only need title and description from the user when creating a job.
        # The 'customer' will be set automatically from the logged-in user.
        fields = ['id', 'title', 'description', 'customer', 'created_at', 'is_completed']
        # Make the customer field read-only in the serializer.
        read_only_fields = ['customer']
from rest_framework import serializers
from .models import User, Job, Bid, Message, ProProfile

class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for the User model.
    """
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'password', 'is_pro', 'full_name', 'phone_number')
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        """
        This method is called when a new user is created.
        We handle the password hashing here.
        """
        password = validated_data.pop('password', None)
        instance = self.Meta.model(**validated_data)
        if password is not None:
            instance.set_password(password)
        instance.save()
        return instance
    
class ProProfileSerializer(serializers.ModelSerializer):
    """
    Serializer for the ProProfile model.
    """
    user = serializers.PrimaryKeyRelatedField(read_only=True)
    full_name = serializers.CharField(source='user.full_name', read_only=True)

    class Meta:
        model = ProProfile
        fields = [
            'id',
            'user',
            'full_name',
            'bio',
            'service_area_zip_codes',
            'profile_picture_url',
        ]
        read_only_fields = ['user', 'full_name']

class BidSerializer(serializers.ModelSerializer):
    """
    Serializer for the Bid model.
    """

    class Meta:
        model = Bid
        fields = ['id', 'job', 'pro', 'amount', 'details', 'created_at']
        read_only_fields = ['job', 'pro']

class JobSerializer(serializers.ModelSerializer):
    """
    Serializer for the Job model.
    """
    bids = BidSerializer(many=True, read_only=True)
    accepted_bid = BidSerializer(read_only=True)

    class Meta:
        model = Job
        fields = ['id', 'title', 'description', 'customer', 'street_address', 'city', 'state', 'zip_code', 'created_at', 'is_completed', 'bids', 'accepted_bid']
        read_only_fields = ['customer']

class MessageSerializer(serializers.ModelSerializer):
    """
    Serializer for the Message model.
    """
    sender_name = serializers.CharField(source='sender.full_name', read_only=True)

    class Meta:
        model = Message
        fields = ['id', 'job', 'sender', 'sender_name', 'receiver', 'body', 'timestamp']
        read_only_fields = ['sender', 'receiver', 'job']
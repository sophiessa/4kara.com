from rest_framework import serializers
from dj_rest_auth.registration.serializers import RegisterSerializer
from allauth.account import app_settings as allauth_settings
from .models import User, Job, Bid, Message, ProProfile


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for the User model.
    """
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'password', 'is_pro', 'first_name', 'last_name', 'phone_number')
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
    user = serializers.PrimaryKeyRelatedField(read_only=True)
    first_name = serializers.CharField(source='user.first_name', read_only=True)
    last_name = serializers.CharField(source='user.last_name', read_only=True)

    class Meta:
        model = ProProfile
        fields = [
            'id',
            'user',
            'first_name',
            'last_name',
            'bio',
            'service_area_zip_codes',
            'profile_picture_url',
            'years_experience',
            'instagram_url',
            'facebook_url',
            'twitter_url',
            'personal_website_url',
            'services_offered',
            'availability_notes',
            'faq',
        ]
        read_only_fields = ['user', 'first_name', 'last_name']


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
    Serializer for the Message model. Includes sender's combined full name.
    """
    sender_name = serializers.SerializerMethodField()

    class Meta:
        model = Message
        fields = ['id', 'job', 'sender', 'sender_name', 'receiver', 'body', 'timestamp']
        read_only_fields = ['sender', 'receiver', 'job']

    def get_sender_name(self, obj):
        first = obj.sender.first_name
        last = obj.sender.last_name
        return f"{first} {last}".strip() or obj.sender.username


class CustomRegisterSerializer(RegisterSerializer):
    is_pro = serializers.BooleanField(default=False)
    first_name = serializers.CharField(max_length=30, required=False, allow_blank=True)
    last_name = serializers.CharField(max_length=150, required=False, allow_blank=True)
    phone_number = serializers.CharField(max_length=20, required=False, allow_blank=True)
    
    def save(self, request):
        user = super().save(request)
        if not user.username:
            user.username = user.email
        user.is_pro = self.validated_data.get('is_pro', False)
        user.first_name = self.validated_data.get('first_name', '')
        user.last_name = self.validated_data.get('last_name', '')
        user.phone_number = self.validated_data.get('phone_number', '')
        user.save() 
        return user
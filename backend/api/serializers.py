from django.db.models import Avg
from rest_framework import serializers
from dj_rest_auth.registration.serializers import RegisterSerializer
from .models import User, Job, Bid, Message, ProProfile, Review


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
    

class BidSerializer(serializers.ModelSerializer):
    """
    Serializer for the Bid model.
    """

    class Meta:
        model = Bid
        fields = ['id', 'job', 'pro', 'amount', 'details', 'created_at']
        read_only_fields = ['job', 'pro']


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
    

class ReviewSerializer(serializers.ModelSerializer):
    """
    Serializer for the Review model.
    """
    customer_name = serializers.CharField(source='customer.get_full_name', read_only=True)
    job_title = serializers.CharField(source='job.title', read_only=True)

    class Meta:
        model = Review
        fields = [
            'id',
            'job',
            'job_title',
            'pro',      
            'customer',   
            'customer_name',
            'rating',   
            'comment',    
            'created_at',
        ]
        read_only_fields = ['pro', 'customer', 'job', 'created_at', 'customer_name']

    def validate_rating(self, value):
        """Ensure rating is between 1 and 5."""
        if not 1 <= value <= 5:
            raise serializers.ValidationError("Rating must be between 1 and 5.")
        return value
    
class JobSerializer(serializers.ModelSerializer):
    """
    Serializer for the Job model.
    """
    bids = BidSerializer(many=True, read_only=True)
    accepted_bid = BidSerializer(read_only=True)
    reviews = ReviewSerializer(many=True, read_only=True)

    class Meta:
        model = Job
        fields = ['id', 'title', 'description', 'customer', 'street_address', 'city', 'state', 'zip_code', 'created_at', 'is_completed', 'bids', 'accepted_bid', 'reviews']
        read_only_fields = ['customer']  


class ProProfileSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(read_only=True)
    first_name = serializers.CharField(source='user.first_name', read_only=True)
    last_name = serializers.CharField(source='user.last_name', read_only=True)
    reviews_received = ReviewSerializer(source='user.reviews_received', many=True, read_only=True)
    average_rating = serializers.SerializerMethodField()

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
            'availability',
            'faq',
            'reviews_received', 
            'average_rating',
        ]
        read_only_fields = ['user', 'first_name', 'last_name']

    def get_average_rating(self, obj):
        avg = obj.user.reviews_received.aggregate(Avg('rating'))['rating__avg']
        return round(avg, 1) if avg is not None else None

          
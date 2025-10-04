from django.contrib.auth.models import User
from rest_framework import serializers
from rest_framework.permissions import AllowAny
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
from user_profile.models import Profile


class RegistrationSerializer(serializers.ModelSerializer):
    repeated_password = serializers.CharField(write_only=True)
    username = serializers.CharField() 
    type = serializers.ChoiceField(choices=[('customer', 'Customer'), ('business', 'Business')], write_only=True)
    
    TYPE_CHOICES = [
        ('customer', 'Customer'),
        ('business', 'Business')
    ]

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'repeated_password', 'type']
        extra_kwargs = {'password': {'write_only': True}}

    def validate_username(self, value):
        if ' ' not in value.strip():
            raise serializers.ValidationError(
                "The name must contain a first and last name, separated by a space")
        return value

    def validate(self, data):
        if data['password'] != data['repeated_password']:
            raise serializers.ValidationError(
                {'error': 'Passwords do not match.'})
        if User.objects.filter(email=data['email']).exists():
            raise serializers.ValidationError(
                {'error': 'A user with this email already exists'}
            )
        return data

    def create(self, validated_data):
        """
        Create and return a new User instance, after removing the repeated_password and type fields.
        Uses email as username (which is Django-compliant) and stores the full name in first_name and last_name fields.
        """
        validated_data.pop('repeated_password')
        user_type = validated_data.pop('type')  
        
        full_name = validated_data.pop('username')  
        email = validated_data['email']
        validated_data['username'] = email
        user = User.objects.create_user(**validated_data)
        
        Profile.objects.create(user=user, type=user_type)

        if full_name:
            try:
                first_name, last_name = full_name.split(' ', 1)
                user.first_name = first_name.capitalize()
                user.last_name = last_name.capitalize()
            except ValueError:
                user.first_name = full_name.capitalize()
                user.last_name = ''
            
            user.save(update_fields=['first_name', 'last_name'])
        user.full_name = full_name
        return user
        
class EmailAuthTokenSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        """
        Validate the provided email and password.
        Checks if a user with the given email exists and if the password is correct.
        If valid, adds the user instance to the validated data.
        """
        email = data.get('email')
        password = data.get('password')

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise serializers.ValidationError(
                "User with this email does not exist")
            
        user = authenticate(username=email, password=password)

        if not user:
            raise serializers.ValidationError("Invalid login credentials.")

        data['user'] = user
        return data
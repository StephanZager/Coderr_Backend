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
    
    def validate(self, data):
        if data['password'] != data['repeated_password']:
            raise serializers.ValidationError(
                {'error': 'Passwords do not match.'})
        if User.objects.filter(email=data['email']).exists():
            raise serializers.ValidationError(
                {'error': 'A user with this email already exists'}
            )
        # Prüfe ob Username bereits existiert
        if User.objects.filter(username=data['username']).exists():
            raise serializers.ValidationError(
                {'error': 'A user with this username already exists'}
            )
        return data

    def create(self, validated_data):
        """
        Create and return a new User instance, keeping the original username.
        Stores the username as-is and extracts first_name/last_name from it.
        """
        validated_data.pop('repeated_password')
        user_type = validated_data.pop('type')  
        
        # Behalte den originalen Username
        original_username = validated_data['username']
        
        # Erstelle User mit dem originalen Username
        user = User.objects.create_user(**validated_data)
        
        Profile.objects.create(user=user, type=user_type)

        # Extrahiere Namen aus dem Username für first_name/last_name
        if original_username:
            try:
                first_name, last_name = original_username.split(' ', 1)
                user.first_name = first_name.capitalize()
                user.last_name = last_name.capitalize()
            except ValueError:
                user.first_name = original_username.capitalize()
                user.last_name = ''
            
            user.save(update_fields=['first_name', 'last_name'])
        
        return user

class EmailAuthTokenSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        """
        Validate the provided username and password.
        """
        username = data.get('username')
        password = data.get('password')

        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            raise serializers.ValidationError(
                "User with this username does not exist")
            
        user = authenticate(username=username, password=password)

        if not user:
            raise serializers.ValidationError("Invalid login credentials.")

        data['user'] = user
        return data
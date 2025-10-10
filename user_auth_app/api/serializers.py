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
        
        
        username_lower = data['username'].lower()
        if User.objects.filter(username=username_lower).exists():
            raise serializers.ValidationError(
                {'error': 'A user with this username already exists'}
            )
        return data

    def create(self, validated_data):
        """
        Create and return a new User instance.
        Stores username in lowercase, but saves original in Profile.
        """
        validated_data.pop('repeated_password')
        user_type = validated_data.pop('type')  
    
        original_username = validated_data['username']
        
        
        validated_data['username'] = original_username.lower()
        
        user = User.objects.create_user(**validated_data)
        
        
        profile = Profile.objects.create(user=user, type=user_type)
        profile.original_username = original_username  
        profile.save()

        if original_username:
            try:
                first_name, last_name = original_username.split(' ', 1)
                user.first_name = first_name.capitalize()
                user.last_name = last_name.capitalize()
            except ValueError:
                user.first_name = original_username.capitalize()
                user.last_name = ''
            
            user.save(update_fields=['first_name', 'last_name'])
        
        
        user._original_username = original_username
        return user
    
    def to_representation(self, instance):
        """
        Return original username in response
        """
        data = super().to_representation(instance)
        
        
        original_username = None
        
        
        if hasattr(instance, '_original_username'):
            original_username = instance._original_username
        else:
            
            try:
                profile = Profile.objects.get(user=instance)
                if hasattr(profile, 'original_username') and profile.original_username:
                    original_username = profile.original_username
            except Profile.DoesNotExist:
                pass
        
        
        if not original_username and instance.first_name:
            if instance.last_name:
                original_username = f"{instance.first_name} {instance.last_name}"
            else:
                original_username = instance.first_name
        
        if original_username:
            data['username'] = original_username
        
        return data

class EmailAuthTokenSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        """
        Validate the provided username and password.
        """
        username = data.get('username')
        password = data.get('password')

        
        username_lower = username.lower()

        try:
            user = User.objects.get(username=username_lower)
        except User.DoesNotExist:
            raise serializers.ValidationError(
                "User with this username does not exist")
            
        user = authenticate(username=username_lower, password=password)  

        if not user:
            raise serializers.ValidationError("Invalid login credentials.")

        data['user'] = user
        return data
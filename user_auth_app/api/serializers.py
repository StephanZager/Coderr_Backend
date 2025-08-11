from django.contrib.auth.models import User
from rest_framework import serializers
from rest_framework.permissions import AllowAny
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate


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
        # The username must contain at least a first and last name, separated by a space.
        # This ensures users provide both names during registration.
        if ' ' not in value.strip():
            raise serializers.ValidationError(
                "The name must contain a first and last name, separated by a space")
        return value

    def validate(self, data):
        # Check if the two password fields match.
        # If not, raise a validation error.
        if data['password'] != data['repeated_password']:
            raise serializers.ValidationError(
                {'error': 'Passwords do not match.'})

        # Check if a user with the given email already exists.
        # If so, raise a validation error.
        if User.objects.filter(email=data['email']).exists():
            raise serializers.ValidationError(
                {'error': 'A user with this email already exists'}
            )

        # We don't check for username uniqueness here since we'll create a unique username
        # from the email address to avoid conflicts with Django's username constraints

        return data

    def create(self, validated_data):
        """
        Create and return a new User instance, after removing the repeated_password and type fields.
        Uses email as username (which is Django-compliant) and stores the full name in first_name and last_name fields.
        """
        # Remove fields that are not needed for user creation
        validated_data.pop('repeated_password')
        user_type = validated_data.pop('type')  # Remove type field
        
        full_name = validated_data.pop('username')  # Get the full name from username field
        email = validated_data['email']
        
        # Use email as Django username to avoid conflicts
        validated_data['username'] = email
        
        # Create the user with the remaining validated data
        user = User.objects.create_user(**validated_data)

        if full_name:
            try:
                # Try to split the full name into first and last name
                first_name, last_name = full_name.split(' ', 1)
                user.first_name = first_name
                user.last_name = last_name
            except ValueError:
                # If splitting fails, set the entire name as first name
                user.first_name = full_name
                user.last_name = ''
            
            user.save(update_fields=['first_name', 'last_name'])

        # Store the full name in a custom attribute for the view to access
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
                "Benutzer mit dieser Email existiert nicht")

        user = authenticate(username=user.username, password=password)

        if not user:
            raise serializers.ValidationError("Ungültige Anmeldedaten.")

        data['user'] = user
        return data        
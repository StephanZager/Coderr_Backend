from django.contrib.auth.models import User
from rest_framework import serializers
from user_profile.models import Profile


class ProfileSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    username = serializers.SerializerMethodField()
    first_name = serializers.CharField(source='user.first_name')
    last_name = serializers.CharField(source='user.last_name')
    email = serializers.CharField(source='user.email')
    created_at = serializers.DateTimeField(
        source='user.date_joined', read_only=True)
    type = serializers.CharField()

    def get_username(self, obj):
        """Generate username from first_name and last_name. Only add underscore if both names exist."""
        first_name = obj.user.first_name.lower()
        last_name = obj.user.last_name.lower()
        
        if first_name and last_name:
            return f"{first_name}_{last_name}"
        elif first_name:
            return first_name
        elif last_name:
            return last_name
        else:
            return ""

    def update(self, instance, validated_data):
        user_data = validated_data.pop('user', None)
        if user_data:
            for attr, value in user_data.items():
                setattr(instance.user, attr, value)
            instance.user.save()
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance

    class Meta:
        model = Profile
        fields = [
            'user',
            'username',
            'first_name',
            'last_name',
            'file',
            'location',
            'tel',
            'description',
            'working_hours',
            'type',
            'email',
            'created_at',
        ]
       


class CustomerSerializer(serializers.ModelSerializer):
    username = serializers.SerializerMethodField()
    first_name = serializers.CharField(source='user.first_name')
    last_name = serializers.CharField(source='user.last_name')
    uploaded_at = serializers.DateTimeField(source='user.date_joined', read_only=True)

    def get_username(self, obj):
        """Generate username from first_name and last_name. Only add underscore if both names exist."""
        first_name = obj.user.first_name.lower()
        last_name = obj.user.last_name.lower()
        
        if first_name and last_name:
            return f"{first_name}_{last_name}"
        elif first_name:
            return first_name
        elif last_name:
            return last_name
        else:
            return ""

    class Meta:
        model = Profile
        fields = [
            'user',
            'username',
            'first_name',
            'last_name',
            'file',
            'uploaded_at',
            'type',
        ]

class BusinessSerializer(serializers.ModelSerializer):
    username = serializers.SerializerMethodField()
    first_name = serializers.CharField(source='user.first_name')
    last_name = serializers.CharField(source='user.last_name')

    def get_username(self, obj):
        """Generate username from first_name and last_name. Only add underscore if both names exist."""
        first_name = obj.user.first_name.lower()
        last_name = obj.user.last_name.lower()
        
        if first_name and last_name:
            return f"{first_name}_{last_name}"
        elif first_name:
            return first_name
        elif last_name:
            return last_name
        else:
            return ""

    class Meta:
        model = Profile
        fields = [
            'user',
            'username',
            'first_name',
            'last_name',
            'file',
            'location',
            'tel',
            'description',
            'working_hours',
            'type',
        ]

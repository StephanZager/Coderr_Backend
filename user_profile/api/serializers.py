from django.contrib.auth.models import User
from rest_framework import serializers
from user_profile.models import Profile


class ProfileSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    username = serializers.SerializerMethodField()
    first_name = serializers.SerializerMethodField()
    last_name = serializers.SerializerMethodField()
    email = serializers.ReadOnlyField(source='user.email')
    created_at = serializers.DateTimeField(source='user.date_joined', read_only=True)
    type = serializers.CharField()

    def get_username(self, obj):
        return f"{obj.user.first_name}_{obj.user.last_name}".lower()
    
    def get_first_name(self, obj):
        return f"{obj.user.first_name}".capitalize()
    
    def get_last_name(self, obj):
        return f"{obj.user.last_name}".capitalize()
        

    class Meta:
        model = Profile
        fields = [
            'user',
            'username',
            'first_name',
            'last_name',
            'location',
            'tel',
            'description',
            'working_hours',
            'type',
            'email',
            'created_at',
        ]



from django.contrib.auth.models import User
from rest_framework import serializers
from user_profile.models import Profile


class ProfileSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    username = serializers.SerializerMethodField()
    first_name = serializers.CharField(source='user.first_name')
    last_name = serializers.CharField(source='user.last_name')
    email = serializers.ReadOnlyField(source='user.email')
    created_at = serializers.DateTimeField(source='user.date_joined', read_only=True)
    type = serializers.CharField()

    def get_username(self, obj):
        return f"{obj.user.first_name}_{obj.user.last_name}".lower()

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



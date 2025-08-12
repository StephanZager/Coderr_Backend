from django.shortcuts import get_object_or_404
from rest_framework import generics, permissions
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import ValidationError, NotFound
from django.contrib.auth.models import User
from user_profile.models import Profile
from user_profile.api.serializers import ProfileSerializer

class ProfileView(generics.RetrieveUpdateAPIView):
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        user_id = self.kwargs.get('user_id')
        return get_object_or_404(Profile, user__id=user_id)
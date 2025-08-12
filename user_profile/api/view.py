from django.shortcuts import get_object_or_404
from rest_framework import generics, permissions
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import ValidationError, NotFound
from django.contrib.auth.models import User
from user_profile.models import Profile
from user_profile.api.serializers import ProfileSerializer, ProfilesSerializer
from .permissions import IsOwner
from rest_framework.generics import ListAPIView

class ProfileView(generics.RetrieveUpdateAPIView):
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer
    permission_classes = [IsAuthenticated, IsOwner]

    def get_object(self):
        user_id = self.kwargs.get('user_id')
        obj = get_object_or_404(Profile, user__id=user_id)
        self.check_object_permissions(self.request, obj)
        return obj
    
class BusinessApiListView(ListAPIView):
    queryset = Profile.objects.filter(type='business')
    serializer_class = ProfilesSerializer
    permission_classes = [IsAuthenticated]
    
class CustomerApiListView(ListAPIView):
    queryset = Profile.objects.filter(type='customer')
    serializer_class = ProfilesSerializer
    permission_classes = [IsAuthenticated]
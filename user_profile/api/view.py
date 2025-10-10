from django.shortcuts import get_object_or_404
from rest_framework import generics, permissions
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import ValidationError, NotFound
from django.contrib.auth.models import User
from user_profile.models import Profile
from user_profile.api.serializers import ProfileSerializer, CustomerSerializer, BusinessSerializer
from .permissions import IsOwner
from rest_framework.generics import ListAPIView

class ProfileView(generics.RetrieveUpdateAPIView):
    """
    API view for retrieving and updating user profiles.
    
    GET: Any authenticated user can view any profile
    PATCH: Only profile owner can update their own profile
    
    Returns profile data with empty strings for null fields.
    """
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer
    permission_classes = [IsAuthenticated]  # Base permission

    def get_permissions(self):
        """
        Return different permissions based on request method.
        
        GET: Only requires authentication
        PATCH/PUT: Requires authentication AND ownership
        """
        if self.request.method in ['PATCH', 'PUT']:
            return [IsAuthenticated(), IsOwner()]
        return [IsAuthenticated()]

    def get_object(self):
        """
        Retrieve profile by user_id with appropriate permission checks.
        """
        user_id = self.kwargs.get('user_id')
        obj = get_object_or_404(Profile, user__id=user_id)
        
        if self.request.method in ['PATCH', 'PUT']:
            self.check_object_permissions(self.request, obj)
            
        return obj
    
class BusinessApiListView(ListAPIView):
    queryset = Profile.objects.filter(type='business')
    serializer_class = BusinessSerializer
    permission_classes = [IsAuthenticated]
    
class CustomerApiListView(ListAPIView):
    queryset = Profile.objects.filter(type='customer')
    serializer_class = CustomerSerializer
    permission_classes = [IsAuthenticated]
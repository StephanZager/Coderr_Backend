from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.views import APIView
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authtoken.views import ObtainAuthToken
from django.contrib.auth.models import User
from rest_framework import generics, permissions

from user_profile.models import Profile
from .serializers import RegistrationSerializer, EmailAuthTokenSerializer


class RegistrationView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegistrationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        token, created = Token.objects.get_or_create(user=user)
        
       
        display_username = user.username
        try:
            profile = Profile.objects.get(user=user)
            if hasattr(profile, 'original_username') and profile.original_username:
                display_username = profile.original_username
            else:
                
                if user.first_name and user.last_name:
                    display_username = f"{user.first_name} {user.last_name}"
                elif user.first_name:
                    display_username = user.first_name
        except Profile.DoesNotExist:
            pass
        
        return Response({
            'token': token.key,
            'username': display_username,  
            'email': user.email,
            'user_id': user.id
        })

class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = EmailAuthTokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        
       
        display_username = user.username
        try:
            profile = Profile.objects.get(user=user)
            if profile.original_username:
                display_username = profile.original_username
        except Profile.DoesNotExist:
            pass
        
        return Response({
            'token': token.key,
            'username': display_username,  
            'email': user.email,
            'user_id': user.id
        })
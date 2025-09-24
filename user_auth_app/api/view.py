from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.views import APIView
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authtoken.views import ObtainAuthToken
from django.contrib.auth.models import User
from rest_framework import generics, permissions
from .serializers import RegistrationSerializer, EmailAuthTokenSerializer


class RegistrationView(APIView):
    """
    API view for user registration.

    Handles POST requests to create a new user account.
    Validates user data using RegistrationSerializer, creates the user and an auth token,
    and returns user information along with the token upon successful registration.
    """
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegistrationSerializer(data=request.data)
        data = {}

        if serializer.is_valid():
            save_account = serializer.save()
            token, created = Token.objects.get_or_create(user=save_account)
            data = {
                'token': token.key,
                'username': getattr(save_account, 'full_name', save_account.username),
                'email': save_account.email,
                'user_id': save_account.id
            }
            return Response(data, status=status.HTTP_201_CREATED)
        else:
            data = serializer.errors
            return Response(data, status=status.HTTP_400_BAD_REQUEST)


class LoginView(ObtainAuthToken):
    """
    API view for user login.
    ...
    """
    permission_classes = [AllowAny] # <-- Diese Zeile wurde hinzugefügt
    serializer_class = EmailAuthTokenSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(
            data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        username = f"{user.first_name} {user.last_name}".strip()

        return Response({
            'token': token.key,
            'username': username,
            'email': user.email,
            'user_id': user.id,
        })

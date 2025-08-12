from django.urls import path
from .view import ProfileView

urlpatterns = [
    path('profile/<int:user_id>/', ProfileView.as_view(), name='profile-by-user'),
]

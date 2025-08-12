from django.urls import path
from .view import ProfileView,BusinessApiListView,CustomerApiListView

urlpatterns = [
    path('profile/<int:user_id>/', ProfileView.as_view(), name='profile-by-user'),
    path('profiles/business/', BusinessApiListView.as_view(), name='all-business-user'),
    path('profiles/customer/', CustomerApiListView.as_view(), name='all-customer-user'),
]

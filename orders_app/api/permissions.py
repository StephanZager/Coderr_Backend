from rest_framework import permissions
from user_profile.models import Profile

class IsCustomerUser(permissions.BasePermission):
    message = "Only customer profiles are allowed to create orders."

    def has_permission(self, request, view):
        user = request.user
        if not user.is_authenticated:
            self.message = "Not authenticated."
            return False
        try:
            profile = user.profile
        except Profile.DoesNotExist:
            self.message = "No profile found."
            return False
        return profile.type == 'customer'

class IsBusinessUser(permissions.BasePermission):
    message = "Only business profiles are allowed to change the status of an order."

    def has_object_permission(self, request, view, obj):
        user = request.user
        if not user.is_authenticated:
            return False
        return obj.business_user == user
from rest_framework import permissions
from user_profile.models import Profile

class IsReviewer(permissions.BasePermission):
    """
    Permission that only allows access to the creator of the review.
    """
    def has_object_permission(self, request, view, obj):
        return obj.reviewer == request.user

class IsCustomerUser(permissions.BasePermission):
    """
    Permission that only allows the user with a 'customer' profile to create a review.
    """
    message = "Only customer profiles are allowed to create reviews."

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
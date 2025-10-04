from rest_framework.permissions import BasePermission


class IsBusinessUser(BasePermission):
    """
    Only allows users with Profile.type == 'business' to create offers.
    Returns appropriate error messages.
    """

    message = "Only business profiles are allowed to create offers."

    def has_permission(self, request, view):
        user = request.user
        if not user.is_authenticated:
            self.message = "Not authenticated."
            return False
        try:
            profile = user.profile
        except AttributeError:
            self.message = "No profile found."
            return False
        if profile.type != 'business':
            self.message = "Only business profiles are allowed to create offers."
            return False
        return True


class IsOwner(BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.user == request.user

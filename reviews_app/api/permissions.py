from rest_framework import permissions
from user_profile.models import Profile

class IsReviewer(permissions.BasePermission):
    """
    Berechtigung, die nur dem Ersteller der Bewertung den Zugriff erlaubt.
    """
    def has_object_permission(self, request, view, obj):
        return obj.reviewer == request.user

class IsCustomerUser(permissions.BasePermission):
    """
    Berechtigung, die nur dem Benutzer mit einem 'customer'-Profil das Erstellen einer Bewertung erlaubt.
    """
    message = "Nur Kunden-Profile dürfen Bewertungen erstellen."

    def has_permission(self, request, view):
        user = request.user
        if not user.is_authenticated:
            self.message = "Nicht authentifiziert."
            return False
        try:
            profile = user.profile
        except Profile.DoesNotExist:
            self.message = "Kein Profil gefunden."
            return False
        return profile.type == 'customer'
from rest_framework import permissions
from user_profile.models import Profile

class IsCustomerUser(permissions.BasePermission):
    message = "Nur Kunden-Profile dürfen Bestellungen erstellen."

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

class IsBusinessUser(permissions.BasePermission):
    message = "Nur Business-Profile dürfen den Status einer Bestellung ändern."

    def has_object_permission(self, request, view, obj):
        user = request.user
        if not user.is_authenticated:
            return False
        return obj.business_user == user
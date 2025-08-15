from rest_framework.permissions import BasePermission

class IsBusinessUser(BasePermission):
    """
    Erlaubt nur User mit Profile.type == 'business' das Erstellen von Angeboten.
    Gibt passende Fehlermeldungen zurück.
    """

    message = "Nur Business-Profile dürfen Angebote erstellen."

    def has_permission(self, request, view):
        user = request.user
        if not user.is_authenticated:
            self.message = "Nicht authentifiziert."
            return False
        try:
            profile = user.profile
        except AttributeError:
            self.message = "Kein Profil gefunden."
            return False
        if profile.type != 'business':
            self.message = "Nur Business-Profile dürfen Angebote erstellen."
            return False
        return True

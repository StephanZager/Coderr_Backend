from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from django.contrib.auth.models import User
from user_profile.models import Profile

class UserProfileTests(APITestCase):

    def setUp(self):
        # Erstelle einen Testbenutzer (Besitzer des Profils) und sein Profil
        self.owner_user = User.objects.create_user(
            username='owner@test.com', email='owner@test.com', password='testpassword'
        )
        self.owner_profile = Profile.objects.create(
            user=self.owner_user, type='business', location='Berlin'
        )
        self.owner_token = self.get_auth_token(self.owner_user, 'testpassword')

        # Erstelle einen anderen Benutzer (Nicht-Besitzer) und sein Profil
        self.other_user = User.objects.create_user(
            username='other@test.com', email='other@test.com', password='testpassword'
        )
        self.other_profile = Profile.objects.create(
            user=self.other_user, type='customer', location='Hamburg'
        )
        self.other_token = self.get_auth_token(self.other_user, 'testpassword')

        # URLs für die Tests
        self.owner_profile_url = reverse('profile-by-user', kwargs={'user_id': self.owner_user.id})
        self.other_profile_url = reverse('profile-by-user', kwargs={'user_id': self.other_user.id})
        self.business_list_url = reverse('all-business-user')
        self.customer_list_url = reverse('all-customer-user')
        
    def get_auth_token(self, user, password):
        # Hilfsmethode zur Anmeldung und zum Abrufen des Tokens
        response = self.client.post(reverse('login'), {'email': user.email, 'password': password})
        if response.status_code != status.HTTP_200_OK:
            raise Exception(f"Login failed for user {user.email}: {response.content.decode()}")
        return response.data['token']

# --- Testfälle für ProfileView ---

    def test_authenticated_user_can_retrieve_own_profile(self):
        """
        Stellt sicher, dass ein authentifizierter Benutzer sein eigenes Profil abrufen kann.
        """
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.owner_token}')
        response = self.client.get(self.owner_profile_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['user'], self.owner_user.id)
        self.assertEqual(response.data['location'], self.owner_profile.location)

    def test_authenticated_user_cannot_retrieve_other_users_profile(self):
        """
        Stellt sicher, dass ein Benutzer nicht das Profil eines anderen Benutzers abrufen kann.
        """
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.owner_token}')
        response = self.client.get(self.other_profile_url)
        # Die API gibt einen 403-Fehler zurück, weil die Berechtigung nicht ausreicht.
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_unauthenticated_user_cannot_retrieve_any_profile(self):
        """
        Stellt sicher, dass ein nicht authentifizierter Benutzer kein Profil abrufen kann.
        """
        self.client.credentials()  # Entferne Token
        response = self.client.get(self.owner_profile_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_owner_can_update_own_profile(self):
        """
        Stellt sicher, dass ein Benutzer sein eigenes Profil aktualisieren kann.
        """
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.owner_token}')
        new_data = {'location': 'Frankfurt'}
        response = self.client.patch(self.owner_profile_url, new_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.owner_profile.refresh_from_db()
        self.assertEqual(self.owner_profile.location, 'Frankfurt')

    def test_non_owner_cannot_update_other_users_profile(self):
        """
        Stellt sicher, dass ein Benutzer nicht das Profil eines anderen Benutzers aktualisieren kann.
        """
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.other_token}')
        new_data = {'location': 'Köln'}
        response = self.client.patch(self.owner_profile_url, new_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_unauthenticated_user_cannot_update_any_profile(self):
        """
        Stellt sicher, dass ein nicht authentifizierter Benutzer kein Profil aktualisieren kann.
        """
        self.client.credentials()
        new_data = {'location': 'Düsseldorf'}
        response = self.client.patch(self.owner_profile_url, new_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

# --- Testfälle für BusinessApiListView ---

    def test_authenticated_user_can_list_business_profiles(self):
        """
        Stellt sicher, dass ein authentifizierter Benutzer alle Business-Profile auflisten kann.
        """
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.other_token}')
        response = self.client.get(self.business_list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['type'], 'business')

    def test_unauthenticated_user_cannot_list_business_profiles(self):
        """
        Stellt sicher, dass ein nicht authentifizierter Benutzer keine Business-Profile auflisten kann.
        """
        self.client.credentials()
        response = self.client.get(self.business_list_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

# --- Testfälle für CustomerApiListView ---

    def test_authenticated_user_can_list_customer_profiles(self):
        """
        Stellt sicher, dass ein authentifizierter Benutzer alle Kunden-Profile auflisten kann.
        """
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.owner_token}')
        response = self.client.get(self.customer_list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['type'], 'customer')

    def test_unauthenticated_user_cannot_list_customer_profiles(self):
        """
        Stellt sicher, dass ein nicht authentifizierter Benutzer keine Kunden-Profile auflisten kann.
        """
        self.client.credentials()
        response = self.client.get(self.customer_list_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
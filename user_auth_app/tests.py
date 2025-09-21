from django.test import TestCase
from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from django.contrib.auth.models import User
from user_profile.models import Profile
from rest_framework.authtoken.models import Token

class UserAuthTests(APITestCase):
    
    def setUp(self):
        # Erstelle ein Benutzerobjekt für die Tests
        self.user = User.objects.create_user(
            username='maxmustermann@test.com',
            email='maxmustermann@test.com',
            password='TestPassword123'
        )
        Profile.objects.create(user=self.user, type='customer')
        self.registration_url = reverse('register')
        self.login_url = reverse('login')
        
# --- Testfälle für die Registrierung (POST /api/registration/) ---

    def test_registration_with_valid_data_creates_user(self):
        """
        Stellt sicher, dass ein neuer Benutzer mit gültigen Daten registriert werden kann.
        """
        data = {
            'username': 'Maria Musterfrau',
            'email': 'maria.musterfrau@test.com',
            'password': 'StrongPassword123',
            'repeated_password': 'StrongPassword123',
            'type': 'business'
        }
        response = self.client.post(self.registration_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('token', response.data)
        self.assertEqual(response.data['email'], 'maria.musterfrau@test.com')
        self.assertEqual(response.data['username'], 'Maria Musterfrau')
        
        # Überprüfen, ob das Profil mit dem korrekten Typ erstellt wurde
        new_user = User.objects.get(email='maria.musterfrau@test.com')
        self.assertTrue(hasattr(new_user, 'profile'))
        self.assertEqual(new_user.profile.type, 'business')

    def test_registration_with_existing_email_fails(self):
        """
        Stellt sicher, dass die Registrierung mit einer bereits existierenden E-Mail fehlschlägt.
        """
        data = {
            'username': 'Another User',
            'email': 'maxmustermann@test.com',
            'password': 'TestPassword123',
            'repeated_password': 'TestPassword123',
            'type': 'customer'
        }
        response = self.client.post(self.registration_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('A user with this email already exists', response.data['error'])

    def test_registration_with_mismatched_passwords_fails(self):
        """
        Stellt sicher, dass die Registrierung fehlschlägt, wenn die Passwörter nicht übereinstimmen.
        """
        data = {
            'username': 'Test User',
            'email': 'testuser@test.com',
            'password': 'PasswordA',
            'repeated_password': 'PasswordB',
            'type': 'customer'
        }
        response = self.client.post(self.registration_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('Passwords do not match.', response.data['error'])

    def test_registration_with_invalid_username_fails(self):
        """
        Stellt sicher, dass die Registrierung fehlschlägt, wenn der Benutzername kein Leerzeichen enthält.
        """
        data = {
            'username': 'InvalidUsername',
            'email': 'invalid@test.com',
            'password': 'TestPassword123',
            'repeated_password': 'TestPassword123',
            'type': 'customer'
        }
        response = self.client.post(self.registration_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('The name must contain a first and last name, separated by a space', response.data['username'][0])

# --- Testfälle für die Anmeldung (POST /api/login/) ---

    def test_login_with_valid_credentials_succeeds(self):
        """
        Stellt sicher, dass sich ein Benutzer mit korrekten Anmeldedaten anmelden kann.
        """
        data = {
            'email': 'maxmustermann@test.com',
            'password': 'TestPassword123'
        }
        response = self.client.post(self.login_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('token', response.data)
        self.assertEqual(response.data['email'], 'maxmustermann@test.com')

    def test_login_with_incorrect_password_fails(self):
        """
        Stellt sicher, dass die Anmeldung mit einem falschen Passwort fehlschlägt.
        """
        data = {
            'email': 'maxmustermann@test.com',
            'password': 'WrongPassword'
        }
        response = self.client.post(self.login_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('Ungültige Anmeldedaten.', response.data['non_field_errors'])

    def test_login_with_non_existent_email_fails(self):
        """
        Stellt sicher, dass die Anmeldung mit einer nicht existierenden E-Mail fehlschlägt.
        """
        data = {
            'email': 'nonexistent@test.com',
            'password': 'TestPassword123'
        }
        response = self.client.post(self.login_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('Benutzer mit dieser Email existiert nicht', response.data['non_field_errors'])

from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from django.contrib.auth.models import User
from user_profile.models import Profile
from .models import Review

class ReviewTests(APITestCase):

    def setUp(self):
        # Erstelle einen Kunden-Benutzer und sein Profil (reviewer)
        self.reviewer_user = User.objects.create_user(
            username='reviewer@test.com', email='reviewer@test.com', password='testpassword'
        )
        Profile.objects.create(user=self.reviewer_user, type='customer')
        self.reviewer_token = self.get_auth_token(self.reviewer_user, 'testpassword')

        # Erstelle einen Business-Benutzer und sein Profil
        self.business_user = User.objects.create_user(
            username='business@test.com', email='business@test.com', password='testpassword'
        )
        Profile.objects.create(user=self.business_user, type='business')
        self.business_token = self.get_auth_token(self.business_user, 'testpassword')

        # Erstelle einen zweiten Business-Benutzer für Tests
        self.other_business_user = User.objects.create_user(
            username='otherbusiness@test.com', email='otherbusiness@test.com', password='testpassword'
        )
        Profile.objects.create(user=self.other_business_user, type='business')
        self.other_business_token = self.get_auth_token(self.other_business_user, 'testpassword')

        # Erstelle eine Beispielbewertung
        self.review = Review.objects.create(
            business_user=self.business_user,
            reviewer=self.reviewer_user,
            rating=5,
            description='Hervorragende Erfahrung!'
        )

    def get_auth_token(self, user, password):
        response = self.client.post(reverse('login'), {'email': user.email, 'password': password})
        if response.status_code != status.HTTP_200_OK:
            raise Exception(f"Login failed for user {user.email}: {response.content.decode()}")
        return response.data['token']

# --- Testfälle für GET /api/reviews/ ---

    def test_authenticated_user_can_list_reviews(self):
        """
        Stellt sicher, dass ein authentifizierter Benutzer die Liste der Bewertungen abrufen kann.
        """
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.reviewer_token}')
        response = self.client.get(reverse('review-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['rating'], self.review.rating)

    def test_unauthenticated_cannot_list_reviews(self):
        """
        Stellt sicher, dass ein nicht authentifizierter Benutzer keine Bewertungen auflisten kann.
        """
        self.client.credentials()
        response = self.client.get(reverse('review-list'))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_list_reviews_with_filters(self):
        """
        Stellt sicher, dass die Liste der Bewertungen nach business_user und reviewer gefiltert werden kann.
        """
        # Erstelle eine weitere Bewertung
        Review.objects.create(
            business_user=self.other_business_user,
            reviewer=self.reviewer_user,
            rating=4,
            description='Solide Arbeit.'
        )
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.reviewer_token}')
        
        # Testen des Filters nach business_user_id
        response = self.client.get(reverse('review-list'), {'business_user': self.business_user.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['business_user'], self.business_user.id)

        # Testen des Filters nach reviewer_id
        response = self.client.get(reverse('review-list'), {'reviewer': self.reviewer_user.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

# --- Testfälle für POST /api/reviews/ ---

    def test_customer_can_create_review(self):
        """
        Stellt sicher, dass ein Kunden-Benutzer eine Bewertung erstellen kann.
        """
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.reviewer_token}')
        data = {
            'business_user': self.other_business_user.id,
            'rating': 3,
            'description': 'Okay, aber nicht mehr.'
        }
        response = self.client.post(reverse('review-list'), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Review.objects.count(), 2)

    def test_customer_cannot_create_duplicate_review(self):
        """
        Stellt sicher, dass ein Kunden-Benutzer keine zweite Bewertung für denselben Geschäftsbenutzer erstellen kann.
        """
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.reviewer_token}')
        data = {
            'business_user': self.business_user.id,
            'rating': 2,
            'description': 'Schlechte Erfahrung.'
        }
        response = self.client.post(reverse('review-list'), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        # Korrigierte Logik, um die Liste der Fehlermeldungen zu überprüfen
        self.assertIn('Sie haben bereits eine Bewertung für diesen Geschäftsbenutzer abgegeben.', str(response.data))

    def test_business_cannot_create_review(self):
        """
        Stellt sicher, dass ein Business-Benutzer keine Bewertung erstellen kann.
        """
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.business_token}')
        data = {
            'business_user': self.other_business_user.id,
            'rating': 5,
            'description': 'Tolle Zusammenarbeit.'
        }
        response = self.client.post(reverse('review-list'), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data['detail'], 'Nur Kunden-Profile dürfen Bewertungen erstellen.')

# --- Testfälle für PATCH /api/reviews/{id}/ ---

    def test_reviewer_can_update_review(self):
        """
        Stellt sicher, dass der Ersteller die Bewertung aktualisieren kann.
        """
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.reviewer_token}')
        data = {'rating': 4, 'description': 'Noch besser als erwartet!'}
        response = self.client.patch(reverse('review-detail', kwargs={'pk': self.review.id}), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.review.refresh_from_db()
        self.assertEqual(self.review.rating, 4)
        self.assertEqual(self.review.description, 'Noch besser als erwartet!')

    def test_non_reviewer_cannot_update_review(self):
        """
        Stellt sicher, dass ein anderer Benutzer eine Bewertung nicht aktualisieren kann.
        """
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.business_token}')
        data = {'rating': 1}
        response = self.client.patch(reverse('review-detail', kwargs={'pk': self.review.id}), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

# --- Testfälle für DELETE /api/reviews/{id}/ ---

    def test_reviewer_can_delete_review(self):
        """
        Stellt sicher, dass der Ersteller eine Bewertung löschen kann.
        """
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.reviewer_token}')
        response = self.client.delete(reverse('review-detail', kwargs={'pk': self.review.id}))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Review.objects.filter(pk=self.review.id).exists())

    def test_non_reviewer_cannot_delete_review(self):
        """
        Stellt sicher, dass ein anderer Benutzer eine Bewertung nicht löschen kann.
        """
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.business_token}')
        response = self.client.delete(reverse('review-detail', kwargs={'pk': self.review.id}))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
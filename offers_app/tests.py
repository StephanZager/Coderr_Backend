from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from django.contrib.auth.models import User
from user_profile.models import Profile
from offers_app.models import Offer, OfferDetail

class OfferTests(APITestCase):

    def setUp(self):
        # Erstelle einen Kunden-Benutzer und sein Profil
        self.customer_user = User.objects.create_user(
            username='customer@test.com', email='customer@test.com', password='testpassword'
        )
        Profile.objects.create(user=self.customer_user, type='customer')
        self.customer_token = self.get_auth_token(self.customer_user, 'testpassword')

        # Erstelle einen Business-Benutzer (Besitzer der Angebote) und sein Profil
        self.business_user = User.objects.create_user(
            username='business@test.com', email='business@test.com', password='testpassword'
        )
        Profile.objects.create(user=self.business_user, type='business')
        self.business_token = self.get_auth_token(self.business_user, 'testpassword')

        # Erstelle einen anderen Business-Benutzer für die Filter-Tests
        self.other_business_user = User.objects.create_user(
            username='otherbusiness@test.com', email='otherbusiness@test.com', password='testpassword'
        )
        Profile.objects.create(user=self.other_business_user, type='business')
        self.other_business_token = self.get_auth_token(self.other_business_user, 'testpassword')

        # Erstelle ein Beispielangebot und zugehörige Details
        self.offer = Offer.objects.create(
            user=self.business_user, 
            title='Webseite erstellen', 
            description='Erstellung einer responsiven Webseite'
        )
        self.offer_detail_1 = OfferDetail.objects.create(
            offer=self.offer,
            title='Basic Package',
            revisions=2,
            delivery_time_in_days=7,
            price=500.00,
            features=['5 Pages', 'Contact Form'],
            offer_type='basic'
        )
        self.offer_detail_2 = OfferDetail.objects.create(
            offer=self.offer,
            title='Pro Package',
            revisions=5,
            delivery_time_in_days=14,
            price=1000.00,
            features=['10 Pages', 'SEO Optimization'],
            offer_type='pro'
        )
        self.offer_detail_3 = OfferDetail.objects.create(
            offer=self.offer,
            title='Premium Package',
            revisions=10,
            delivery_time_in_days=21,
            price=2000.00,
            features=['20 Pages', 'E-commerce'],
            offer_type='premium'
        )

        # URLs für die Tests
        self.offer_list_url = reverse('offer-list')
        self.offer_detail_url = reverse('offer-detail', kwargs={'pk': self.offer.id})

    def get_auth_token(self, user, password):
        # Hilfsmethode zur Anmeldung und zum Abrufen des Tokens
        response = self.client.post(reverse('login'), {'email': user.email, 'password': password})
        if response.status_code != status.HTTP_200_OK:
            raise Exception(f"Login failed for user {user.email}: {response.content.decode()}")
        return response.data['token']

# --- Testfälle für OfferView (GET, POST) ---

    def test_authenticated_user_can_list_offers(self):
        """
        Stellt sicher, dass ein authentifizierter Benutzer Angebote auflisten kann.
        """
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.customer_token}')
        response = self.client.get(self.offer_list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('results', response.data)
        self.assertGreater(len(response.data['results']), 0)
        self.assertEqual(response.data['results'][0]['title'], self.offer.title)

    def test_unauthenticated_user_can_list_offers(self):
        """
        Stellt sicher, dass ein nicht authentifizierter Benutzer Angebote auflisten kann.
        (IsAuthenticatedOrReadOnly)
        """
        self.client.credentials()
        response = self.client.get(self.offer_list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('results', response.data)

    def test_business_user_can_create_offer(self):
        """
        Stellt sicher, dass ein Business-Benutzer ein Angebot erstellen kann.
        """
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.business_token}')
        data = {
            'title': 'App Entwicklung',
            'description': 'Entwicklung einer mobilen App',
            'details': [
                {'title': 'Basic', 'revisions': 2, 'delivery_time_in_days': 10, 'price': 1000.00, 'features': [], 'offer_type': 'basic'},
                {'title': 'Pro', 'revisions': 5, 'delivery_time_in_days': 20, 'price': 2500.00, 'features': [], 'offer_type': 'pro'},
                {'title': 'Premium', 'revisions': 99, 'delivery_time_in_days': 30, 'price': 5000.00, 'features': [], 'offer_type': 'premium'}
            ]
        }
        response = self.client.post(self.offer_list_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Offer.objects.count(), 2)
        self.assertEqual(OfferDetail.objects.count(), 6)

    def test_customer_cannot_create_offer(self):
        """
        Stellt sicher, dass ein Kunden-Benutzer kein Angebot erstellen kann.
        """
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.customer_token}')
        data = {
            'title': 'Neues Angebot',
            'description': 'Beschreibung',
            'details': []
        }
        response = self.client.post(self.offer_list_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data['detail'], 'Nur Business-Profile dürfen Angebote erstellen.')

    def test_unauthenticated_user_cannot_create_offer(self):
        """
        Stellt sicher, dass ein nicht authentifizierter Benutzer kein Angebot erstellen kann.
        """
        self.client.credentials()
        data = {
            'title': 'Test Angebot',
            'description': 'Beschreibung',
            'details': []
        }
        response = self.client.post(self.offer_list_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_offer_with_wrong_number_of_details_fails(self):
        """
        Stellt sicher, dass die Erstellung fehlschlägt, wenn die Anzahl der Details nicht 3 beträgt.
        """
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.business_token}')
        data = {
            'title': 'Test Angebot',
            'description': 'Beschreibung',
            'details': [
                {'title': 'Basic', 'revisions': 2, 'delivery_time_in_days': 10, 'price': 100.00, 'features': [], 'offer_type': 'basic'},
                {'title': 'Pro', 'revisions': 5, 'delivery_time_in_days': 20, 'price': 200.00, 'features': [], 'offer_type': 'pro'}
            ]
        }
        response = self.client.post(self.offer_list_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['error'], 'Ein Angebot muss genau 3 Details enthalten.')

# --- Testfälle für OfferDetailView (GET, PATCH, PUT, DELETE) ---

    def test_owner_can_retrieve_offer_detail(self):
        """
        Stellt sicher, dass der Besitzer ein spezifisches Angebot abrufen kann.
        """
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.business_token}')
        response = self.client.get(self.offer_detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], self.offer.title)

    def test_non_owner_can_retrieve_offer_detail(self):
        """
        Stellt sicher, dass ein Nicht-Besitzer ein spezifisches Angebot abrufen kann.
        """
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.customer_token}')
        response = self.client.get(self.offer_detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], self.offer.title)

    def test_unauthenticated_cannot_retrieve_offer_detail(self):
        """
        Stellt sicher, dass ein nicht authentifizierter Benutzer ein Angebot nicht abrufen kann.
        """
        self.client.credentials()
        response = self.client.get(self.offer_detail_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_owner_can_update_offer(self):
        """
        Stellt sicher, dass der Besitzer ein Angebot aktualisieren kann.
        """
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.business_token}')
        updated_data = {
            'title': 'Webseite aktualisiert',
            'description': 'Beschreibung aktualisiert',
        }
        response = self.client.patch(self.offer_detail_url, updated_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.offer.refresh_from_db()
        self.assertEqual(self.offer.title, 'Webseite aktualisiert')

    def test_non_owner_cannot_update_offer(self):
        """
        Stellt sicher, dass ein Nicht-Besitzer ein Angebot nicht aktualisieren kann.
        """
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.customer_token}')
        updated_data = {'title': 'Titel geändert'}
        response = self.client.patch(self.offer_detail_url, updated_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_owner_can_delete_offer(self):
        """
        Stellt sicher, dass der Besitzer ein Angebot löschen kann.
        """
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.business_token}')
        response = self.client.delete(self.offer_detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Offer.objects.filter(id=self.offer.id).exists())
        self.assertFalse(OfferDetail.objects.filter(offer=self.offer).exists())

    def test_non_owner_cannot_delete_offer(self):
        """
        Stellt sicher, dass ein Nicht-Besitzer ein Angebot nicht löschen kann.
        """
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.customer_token}')
        response = self.client.delete(self.offer_detail_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

# --- Testfälle für OfferDetailObjView ---
# Testet den spezifischen Endpunkt zum Abrufen eines einzelnen OfferDetail-Objekts.

    def test_authenticated_user_can_retrieve_offer_detail_object(self):
        """
        Stellt sicher, dass ein authentifizierter Benutzer ein einzelnes OfferDetail-Objekt abrufen kann.
        """
        url = reverse('offerdetail-detail', kwargs={'pk': self.offer_detail_1.id})
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.customer_token}')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Basic Package')
        self.assertEqual(response.data['offer_type'], 'basic')
        
    def test_unauthenticated_user_cannot_retrieve_offer_detail_object(self):
        """
        Stellt sicher, dass ein nicht authentifizierter Benutzer kein einzelnes OfferDetail-Objekt abrufen kann.
        """
        url = reverse('offerdetail-detail', kwargs={'pk': self.offer_detail_1.id})
        self.client.credentials()
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
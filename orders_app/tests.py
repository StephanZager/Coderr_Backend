from rest_framework import status
from rest_framework.test import APITestCase
from django.urls import reverse
from django.contrib.auth.models import User
from user_profile.models import Profile
from offers_app.models import Offer, OfferDetail
from orders_app.models import Order

class OrderTests(APITestCase):

    def setUp(self):
        # Erstelle einen Kunden-Benutzer und ein Profil
        self.customer_user = User.objects.create_user(
            username='customer@example.com', email='customer@example.com', password='password123'
        )
        self.customer_profile = Profile.objects.create(
            user=self.customer_user, type='customer'
        )
        self.customer_token = self.get_auth_token(self.customer_user, 'password123')

        # Erstelle einen Business-Benutzer und ein Profil
        self.business_user = User.objects.create_user(
            username='business@example.com', email='business@example.com', password='password123'
        )
        self.business_profile = Profile.objects.create(
            user=self.business_user, type='business'
        )
        self.business_token = self.get_auth_token(self.business_user, 'password123')

        # Erstelle einen Admin-Benutzer
        self.admin_user = User.objects.create_superuser(
            username='admin@example.com', email='admin@example.com', password='adminpassword'
        )
        self.admin_token = self.get_auth_token(self.admin_user, 'adminpassword')

        # Erstelle ein Angebot und ein OfferDetail-Objekt für Tests
        self.offer = Offer.objects.create(
            user=self.business_user, title='Test Offer', description='Test Description'
        )
        self.offer_detail = OfferDetail.objects.create(
            offer=self.offer,
            title='Test Offer Detail',
            revisions=3,
            delivery_time_in_days=5,
            price=150.00,
            features=['Feature 1', 'Feature 2'],
            offer_type='basic'
        )

        # Erstelle eine Beispielbestellung für die Tests
        self.order = Order.objects.create(
            customer_user=self.customer_user,
            business_user=self.business_user,
            title='Order Title',
            revisions=1,
            delivery_time_in_days=2,
            price=100.00,
            features=['Feature A'],
            offer_type='standard',
            status='in_progress'
        )

    def get_auth_token(self, user, password):
        # Authentifizierung und Login
        response = self.client.post(reverse('login'), {'email': user.email, 'password': password})
        # Sicherstellen, dass die Anmeldung erfolgreich war, bevor der Token zurückgegeben wird
        if response.status_code != status.HTTP_200_OK:
            # Wenn die Anmeldung fehlschlägt, den Fehler ausgeben, um die Ursache zu finden
            raise Exception(f"Fehler bei der Anmeldung für Benutzer {user.email}: {response.content.decode()}")
        return response.data['token']

    def tearDown(self):
        self.client.logout()

# --- Testfälle für POST /api/orders/ ---

    def test_customer_can_create_order(self):
        """
        Stellt sicher, dass ein Kunden-Benutzer eine Bestellung erstellen kann.
        """
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.customer_token}')
        data = {'offer_detail_id': self.offer_detail.id}
        response = self.client.post(reverse('order-list'), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['title'], self.offer_detail.title)
        self.assertEqual(response.data['customer_user']['username'], self.customer_user.username)

    def test_business_cannot_create_order(self):
        """
        Stellt sicher, dass ein Business-Benutzer keine Bestellung erstellen kann.
        """
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.business_token}')
        data = {'offer_detail_id': self.offer_detail.id}
        response = self.client.post(reverse('order-list'), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data['detail'], 'Nur Kunden-Profile dürfen Bestellungen erstellen.')

    def test_unauthenticated_cannot_create_order(self):
        """
        Stellt sicher, dass ein nicht authentifizierter Benutzer keine Bestellung erstellen kann.
        """
        self.client.credentials()  # Entferne Token
        data = {'offer_detail_id': self.offer_detail.id}
        response = self.client.post(reverse('order-list'), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_order_with_invalid_offer_detail_id(self):
        """
        Stellt sicher, dass eine ungültige Angebots-ID einen 404-Fehler zurückgibt.
        """
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.customer_token}')
        data = {'offer_detail_id': 9999}
        response = self.client.post(reverse('order-list'), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data['error'], 'Das angegebene Angebotsdetail wurde nicht gefunden.')

# --- Testfälle für GET /api/orders/ ---

    def test_get_customer_orders(self):
        """
        Stellt sicher, dass ein Kunden-Benutzer seine eigenen Bestellungen sehen kann.
        """
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.customer_token}')
        response = self.client.get(reverse('order-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['id'], self.order.id)

    def test_get_business_orders(self):
        """
        Stellt sicher, dass ein Business-Benutzer Bestellungen sehen kann, bei denen er der Geschäftspartner ist.
        """
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.business_token}')
        response = self.client.get(reverse('order-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['id'], self.order.id)

    def test_unauthenticated_cannot_get_orders(self):
        """
        Stellt sicher, dass ein nicht authentifizierter Benutzer keine Bestellliste abrufen kann.
        """
        self.client.credentials()
        response = self.client.get(reverse('order-list'))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

# --- Testfälle für PATCH /api/orders/{id}/ ---

    def test_business_can_update_order_status(self):
        """
        Stellt sicher, dass ein Business-Benutzer den Status einer Bestellung aktualisieren kann.
        """
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.business_token}')
        data = {'status': 'completed'}
        response = self.client.patch(reverse('order-detail', kwargs={'pk': self.order.id}), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.order.refresh_from_db()
        self.assertEqual(self.order.status, 'completed')

    def test_customer_cannot_update_order_status(self):
        """
        Stellt sicher, dass ein Kunden-Benutzer den Status einer Bestellung nicht aktualisieren kann.
        """
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.customer_token}')
        data = {'status': 'completed'}
        response = self.client.patch(reverse('order-detail', kwargs={'pk': self.order.id}), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data['detail'], 'Sie haben keine Berechtigung, diese Aktion durchzuführen.')

    def test_unauthenticated_cannot_update_order(self):
        """
        Stellt sicher, dass ein nicht authentifizierter Benutzer eine Bestellung nicht aktualisieren kann.
        """
        self.client.credentials()
        data = {'status': 'completed'}
        response = self.client.patch(reverse('order-detail', kwargs={'pk': self.order.id}), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

# --- Testfälle für DELETE /api/orders/{id}/ ---

    def test_admin_can_delete_order(self):
        """
        Stellt sicher, dass ein Admin-Benutzer eine Bestellung löschen kann.
        """
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.admin_token}')
        response = self.client.delete(reverse('order-detail', kwargs={'pk': self.order.id}))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Order.objects.filter(pk=self.order.id).exists())

    def test_non_admin_cannot_delete_order(self):
        """
        Stellt sicher, dass ein Nicht-Admin-Benutzer keine Bestellung löschen kann.
        """
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.customer_token}')
        response = self.client.delete(reverse('order-detail', kwargs={'pk': self.order.id}))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

# --- Testfälle für GET /api/order-count/{business_user_id}/ ---

    def test_get_order_count(self):
        """
        Stellt sicher, dass ein authentifizierter Benutzer die Anzahl der laufenden Bestellungen eines Geschäftspartners abrufen kann.
        """
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.customer_token}')
        Order.objects.create(business_user=self.business_user, status='in_progress', title='Another Order', revisions=1, delivery_time_in_days=1, price=50, features=[], offer_type='basic')
        response = self.client.get(reverse('order-count', kwargs={'business_user_id': self.business_user.id}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['order_count'], 2)

    def test_get_order_count_for_non_existent_user(self):
        """
        Stellt sicher, dass eine Anfrage mit einer ungültigen ID einen 404-Fehler zurückgibt.
        """
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.customer_token}')
        response = self.client.get(reverse('order-count', kwargs={'business_user_id': 9999}))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

# --- Testfälle für GET /api/completed-order-count/{business_user_id}/ ---

    def test_get_completed_order_count(self):
        """
        Stellt sicher, dass ein authentifizierter Benutzer die Anzahl der abgeschlossenen Bestellungen abrufen kann.
        """
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.business_token}')
        Order.objects.create(business_user=self.business_user, status='completed', title='Completed Order', revisions=1, delivery_time_in_days=1, price=50, features=[], offer_type='basic')
        response = self.client.get(reverse('completed-order-count', kwargs={'business_user_id': self.business_user.id}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['completed_order_count'], 1)

    def test_get_completed_order_count_for_non_existent_user(self):
        """
        Stellt sicher, dass eine Anfrage mit einer ungültigen ID einen 404-Fehler zurückgibt.
        """
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.business_token}')
        response = self.client.get(reverse('completed-order-count', kwargs={'business_user_id': 9999}))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
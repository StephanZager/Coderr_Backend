from rest_framework import status
from rest_framework.test import APITestCase
from django.urls import reverse
from django.contrib.auth.models import User
from user_profile.models import Profile
from offers_app.models import Offer, OfferDetail
from orders_app.models import Order

class OrderTests(APITestCase):
    """
    Test suite for Order API endpoints.
    
    Tests CRUD operations, permissions, authentication, and business logic
    for orders including creation from offer details, status updates, and
    order count statistics.
    """

    def setUp(self):
        """
        Set up test data including users, profiles, offers, offer details, and orders.
        Creates customer, business, and admin users with authentication tokens.
        """
        # Create customer user and profile
        self.customer_user = User.objects.create_user(
            username='customer@example.com', email='customer@example.com', password='testpassword'
        )
        self.customer_profile = Profile.objects.create(
            user=self.customer_user, type='customer'
        )
        self.customer_token = self.get_auth_token(self.customer_user, 'testpassword')

        # Create business user and profile
        self.business_user = User.objects.create_user(
            username='business@example.com', email='business@example.com', password='testpassword'
        )
        self.business_profile = Profile.objects.create(
            user=self.business_user, type='business'
        )
        self.business_token = self.get_auth_token(self.business_user, 'testpassword')

        # Create admin user
        self.admin_user = User.objects.create_superuser(
            username='admin@example.com', email='admin@example.com', password='adminpassword'
        )
        self.admin_token = self.get_auth_token(self.admin_user, 'adminpassword')

        # Create offer and offer detail for tests
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

        # Create sample order for tests
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
        """
        Authenticate user and return authentication token.
        
        Args:
            user: User object to authenticate
            password: User's password
            
        Returns:
            str: Authentication token
            
        Raises:
            Exception: If login fails
        """
        response = self.client.post(reverse('login'), {'email': user.email, 'password': password})
        if response.status_code != status.HTTP_200_OK:
            raise Exception(f"Login failed for user {user.email}: {response.content.decode()}")
        return response.data['token']

    # --- Test cases for GET /api/orders/ ---

    def test_authenticated_user_can_list_their_orders_as_customer(self):
        """
        Ensures that a customer user can view their own orders.
        """
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.customer_token}')
        response = self.client.get(reverse('order-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['id'], self.order.id)

    def test_authenticated_user_can_list_their_orders_as_business_user(self):
        """
        Ensures that a business user can view orders where they are the business partner.
        """
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.business_token}')
        response = self.client.get(reverse('order-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['id'], self.order.id)

    def test_unauthenticated_cannot_list_orders(self):
        """
        Ensures that an unauthenticated user cannot retrieve order list.
        """
        self.client.credentials()
        response = self.client.get(reverse('order-list'))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    # --- Test cases for POST /api/orders/ ---

    def test_customer_can_create_order(self):
        """
        Ensures that a customer user can create an order.
        """
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.customer_token}')
        data = {'offer_detail_id': self.offer_detail.id}
        response = self.client.post(reverse('order-list'), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['title'], self.offer_detail.title)
        self.assertEqual(response.data['customer_user'], self.customer_user.id)

    def test_business_cannot_create_order(self):
        """
        Ensures that a business user cannot create an order.
        """
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.business_token}')
        data = {'offer_detail_id': self.offer_detail.id}
        response = self.client.post(reverse('order-list'), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data['detail'], 'Nur Kunden-Profile dürfen Bestellungen erstellen.')

    def test_unauthenticated_cannot_create_order(self):
        """
        Ensures that an unauthenticated user cannot create an order.
        """
        self.client.credentials()
        data = {'offer_detail_id': self.offer_detail.id}
        response = self.client.post(reverse('order-list'), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_order_with_invalid_offer_detail_id(self):
        """
        Ensures that an invalid offer ID returns a 404 error.
        """
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.customer_token}')
        data = {'offer_detail_id': 9999}
        response = self.client.post(reverse('order-list'), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data['detail'], 'Das angegebene Angebotsdetail wurde nicht gefunden.')

    # --- Test cases for PATCH /api/orders/{id}/ ---

    def test_business_can_update_order_status(self):
        """
        Ensures that a business user can update an order status.
        """
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.business_token}')
        data = {'status': 'completed'}
        response = self.client.patch(reverse('order-detail', kwargs={'pk': self.order.id}), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.order.refresh_from_db()
        self.assertEqual(self.order.status, 'completed')

    def test_customer_cannot_update_order_status(self):
        """
        Ensures that a customer user cannot update an order status.
        """
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.customer_token}')
        data = {'status': 'completed'}
        response = self.client.patch(reverse('order-detail', kwargs={'pk': self.order.id}), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data['detail'], 'Nur Business-Profile dürfen den Status einer Bestellung ändern.')

    def test_unauthenticated_cannot_update_order(self):
        """
        Ensures that an unauthenticated user cannot update an order.
        """
        self.client.credentials()
        data = {'status': 'completed'}
        response = self.client.patch(reverse('order-detail', kwargs={'pk': self.order.id}), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    # --- Test cases for DELETE /api/orders/{id}/ ---

    def test_admin_can_delete_order(self):
        """
        Ensures that an admin user can delete an order.
        """
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.admin_token}')
        response = self.client.delete(reverse('order-detail', kwargs={'pk': self.order.id}))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Order.objects.filter(pk=self.order.id).exists())

    def test_non_admin_cannot_delete_order(self):
        """
        Ensures that a non-admin user cannot delete an order.
        """
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.customer_token}')
        response = self.client.delete(reverse('order-detail', kwargs={'pk': self.order.id}))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    # --- Test cases for GET /api/order-count/{business_user_id}/ ---

    def test_get_order_count(self):
        """
        Ensures that an authenticated user can retrieve the count of ongoing orders for a business partner.
        """
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.customer_token}')
        Order.objects.create(business_user=self.business_user, status='in_progress', title='Another Order', revisions=1, delivery_time_in_days=1, price=50, features=[], offer_type='basic', customer_user=self.customer_user)
        response = self.client.get(reverse('order-count', kwargs={'business_user_id': self.business_user.id}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['order_count'], 2)

    def test_get_order_count_for_non_existent_business_user(self):
        """
        Ensures that a request with an invalid ID returns a 404 error.
        """
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.customer_token}')
        response = self.client
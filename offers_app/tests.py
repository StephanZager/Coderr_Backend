from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from django.contrib.auth.models import User
from user_profile.models import Profile
from offers_app.models import Offer, OfferDetail

class OfferTests(APITestCase):
    """
    Test suite for Offer API endpoints.
    
    Tests CRUD operations, permissions, authentication, and business logic
    for offers and offer details including proper error handling.
    """

    def setUp(self):
        """
        Set up test data including users, profiles, offers and offer details.
        Creates customer and business users with authentication tokens.
        """
        self.customer_user = User.objects.create_user(
            username='customer@test.com', email='customer@test.com', password='testpassword'
        )
        Profile.objects.create(user=self.customer_user, type='customer')
        self.customer_token = self.get_auth_token(self.customer_user, 'testpassword')

        self.business_user = User.objects.create_user(
            username='business@test.com', email='business@test.com', password='testpassword'
        )
        Profile.objects.create(user=self.business_user, type='business')
        self.business_token = self.get_auth_token(self.business_user, 'testpassword')

        self.other_business_user = User.objects.create_user(
            username='otherbusiness@test.com', email='otherbusiness@test.com', password='testpassword'
        )
        Profile.objects.create(user=self.other_business_user, type='business')
        self.other_business_token = self.get_auth_token(self.other_business_user, 'testpassword')

        self.offer = Offer.objects.create(
            user=self.business_user, 
            title='Website Creation', 
            description='Creation of a responsive website'
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

        self.offer_list_url = reverse('offer-list')
        self.offer_detail_url = reverse('offer-detail', kwargs={'pk': self.offer.id})

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

    def test_authenticated_user_can_list_offers(self):
        """
        Ensures that an authenticated user can list offers.
        """
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.customer_token}')
        response = self.client.get(self.offer_list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('results', response.data)
        self.assertGreater(len(response.data['results']), 0)
        self.assertEqual(response.data['results'][0]['title'], self.offer.title)

    def test_unauthenticated_user_can_list_offers(self):
        """
        Ensures that an unauthenticated user can list offers.
        (IsAuthenticatedOrReadOnly)
        """
        self.client.credentials()
        response = self.client.get(self.offer_list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('results', response.data)

    def test_business_user_can_create_offer(self):
        """
        Ensures that a business user can create an offer.
        """
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.business_token}')
        data = {
            'title': 'App Development',
            'description': 'Development of a mobile app',
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
        Ensures that a customer user cannot create an offer.
        """
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.customer_token}')
        data = {
            'title': 'New Offer',
            'description': 'Description',
            'details': []
        }
        response = self.client.post(self.offer_list_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data['detail'], 'Nur Business-Profile dürfen Angebote erstellen.')

    def test_unauthenticated_user_cannot_create_offer(self):
        """
        Ensures that an unauthenticated user cannot create an offer.
        """
        self.client.credentials()
        data = {
            'title': 'Test Offer',
            'description': 'Description',
            'details': []
        }
        response = self.client.post(self.offer_list_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_offer_with_wrong_number_of_details_fails(self):
        """
        Ensures that creation fails when the number of details is not 3.
        """
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.business_token}')
        data = {
            'title': 'Test Offer',
            'description': 'Description',
            'details': [
                {'title': 'Basic', 'revisions': 2, 'delivery_time_in_days': 10, 'price': 100.00, 'features': [], 'offer_type': 'basic'},
                {'title': 'Pro', 'revisions': 5, 'delivery_time_in_days': 20, 'price': 200.00, 'features': [], 'offer_type': 'pro'}
            ]
        }
        response = self.client.post(self.offer_list_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['error'], 'Ein Angebot muss genau 3 Details enthalten.')

    def test_owner_can_retrieve_offer_detail(self):
        """
        Ensures that the owner can retrieve a specific offer.
        """
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.business_token}')
        response = self.client.get(self.offer_detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], self.offer.title)

    def test_non_owner_can_retrieve_offer_detail(self):
        """
        Ensures that a non-owner can retrieve a specific offer.
        """
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.customer_token}')
        response = self.client.get(self.offer_detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], self.offer.title)

    def test_unauthenticated_cannot_retrieve_offer_detail(self):
        """
        Ensures that an unauthenticated user cannot retrieve an offer.
        """
        self.client.credentials()
        response = self.client.get(self.offer_detail_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_owner_can_update_offer(self):
        """
        Ensures that the owner can update an offer.
        """
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.business_token}')
        updated_data = {
            'title': 'Website Updated',
            'description': 'Description Updated',
        }
        response = self.client.patch(self.offer_detail_url, updated_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.offer.refresh_from_db()
        self.assertEqual(self.offer.title, 'Website Updated')

    def test_non_owner_cannot_update_offer(self):
        """
        Ensures that a non-owner cannot update an offer.
        """
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.customer_token}')
        updated_data = {'title': 'Title Changed'}
        response = self.client.patch(self.offer_detail_url, updated_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_owner_can_delete_offer(self):
        """
        Ensures that the owner can delete an offer.
        """
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.business_token}')
        response = self.client.delete(self.offer_detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Offer.objects.filter(id=self.offer.id).exists())
        self.assertFalse(OfferDetail.objects.filter(offer=self.offer).exists())

    def test_non_owner_cannot_delete_offer(self):
        """
        Ensures that a non-owner cannot delete an offer.
        """
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.customer_token}')
        response = self.client.delete(self.offer_detail_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_authenticated_user_can_retrieve_offer_detail_object(self):
        """
        Ensures that an authenticated user can retrieve a single OfferDetail object.
        """
        url = reverse('offerdetail-detail', kwargs={'pk': self.offer_detail_1.id})
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.customer_token}')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Basic Package')
        self.assertEqual(response.data['offer_type'], 'basic')
        
    def test_unauthenticated_user_cannot_retrieve_offer_detail_object(self):
        """
        Ensures that an unauthenticated user cannot retrieve a single OfferDetail object.
        """
        url = reverse('offerdetail-detail', kwargs={'pk': self.offer_detail_1.id})
        self.client.credentials()
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
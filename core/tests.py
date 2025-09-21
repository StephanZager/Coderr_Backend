from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from django.contrib.auth.models import User
from user_profile.models import Profile
from offers_app.models import Offer
from reviews_app.models import Review

class BaseInfoTests(APITestCase):

    def setUp(self):
        # Erstelle Testdaten in den verschiedenen Apps
        self.customer_user = User.objects.create_user(
            username='customer@test.com', email='customer@test.com', password='testpassword'
        )
        self.business_user = User.objects.create_user(
            username='business@test.com', email='business@test.com', password='testpassword'
        )
        self.other_business_user = User.objects.create_user(
            username='otherbusiness@test.com', email='otherbusiness@test.com', password='testpassword'
        )

        Profile.objects.create(user=self.customer_user, type='customer')
        Profile.objects.create(user=self.business_user, type='business')
        Profile.objects.create(user=self.other_business_user, type='business')
        
        Offer.objects.create(user=self.business_user, title='Offer 1')
        Offer.objects.create(user=self.other_business_user, title='Offer 2')

        Review.objects.create(
            business_user=self.business_user, reviewer=self.customer_user, rating=5, description='Great'
        )
        Review.objects.create(
            business_user=self.other_business_user, reviewer=self.customer_user, rating=4, description='Good'
        )

    def test_base_info_endpoint_returns_correct_data(self):
        """
        Stellt sicher, dass der base-info-Endpunkt korrekte statistische Daten zurückgibt.
        """
        url = reverse('base-info')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['review_count'], 2)
        self.assertEqual(response.data['average_rating'], 4.5)
        self.assertEqual(response.data['business_profile_count'], 2)
        self.assertEqual(response.data['offer_count'], 2)

    def test_base_info_with_no_data(self):
        """
        Stellt sicher, dass der Endpunkt korrekte Daten zurückgibt, wenn keine Objekte vorhanden sind.
        """
        Review.objects.all().delete()
        Profile.objects.all().delete()
        Offer.objects.all().delete()

        url = reverse('base-info')
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['review_count'], 0)
        self.assertEqual(response.data['average_rating'], 0.0)
        self.assertEqual(response.data['business_profile_count'], 0)
        self.assertEqual(response.data['offer_count'], 0)
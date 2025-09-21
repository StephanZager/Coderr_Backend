from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Count, Avg
from offers_app.models import Offer
from user_profile.models import Profile
from reviews_app.models import Review


class BaseInfoView(APIView):
    """
    Ruft allgemeine Basisinformationen zur Plattform ab.
    """
    def get(self, request):
        try:
            # Anzahl der Bewertungen
            review_count = Review.objects.count()
            
            # Durchschnittliche Bewertung
            average_rating_data = Review.objects.aggregate(avg_rating=Avg('rating'))
            average_rating = round(average_rating_data.get('avg_rating', 0), 1) if average_rating_data.get('avg_rating') is not None else 0.0

            # Anzahl der Geschäftsnutzer
            business_profile_count = Profile.objects.filter(type='business').count()

            # Anzahl der Angebote
            offer_count = Offer.objects.count()

            data = {
                "review_count": review_count,
                "average_rating": average_rating,
                "business_profile_count": business_profile_count,
                "offer_count": offer_count
            }
            return Response(data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
import django_filters
from .models import Offer

class OfferFilter(django_filters.FilterSet):
    
    creator_id = django_filters.NumberFilter(field_name='user')

    # Name in URL: 'min_price' -> Model-Feld: 'price' (größer/gleich)
    min_price = django_filters.NumberFilter(field_name='price', lookup_expr='gte')

    # Name in URL: 'max_delivery_time' -> Model-Feld: 'delivery_time' (kleiner/gleich)
    max_delivery_time = django_filters.NumberFilter(field_name='delivery_time', lookup_expr='lte')

    class Meta:
        model = Offer
        # Wir definieren alle Felder oben explizit, daher kann 'fields' hier leer bleiben.
        fields = ['creator_id', 'min_price', 'max_delivery_time']

    
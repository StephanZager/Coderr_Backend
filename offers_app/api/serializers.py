from django.contrib.auth.models import User
from rest_framework import serializers
from ..models import Offer, OfferDetail
from django.db.models import Min


class OfferDetailListSerializer(serializers.ModelSerializer):
    """
    Serializer for listing offer details with minimal information.
    Used in offer list views to provide basic detail info and URL reference.
    """
    url = serializers.SerializerMethodField()

    class Meta:
        model = OfferDetail
        fields = ['id', 'url']

    def get_url(self, obj):
        """
        Generate relative URL path for the offer detail object.
        Returns: Relative URL string in format '/offerdetails/{id}/'
        """
        return f"/offerdetails/{obj.id}/"

class OfferDetailRetrieveListSerializer(serializers.ModelSerializer):
    """
    Serializer for offer details in retrieve views with full URL information.
    Used when displaying individual offers to provide complete detail URLs.
    """
    url = serializers.SerializerMethodField()

    class Meta:
        model = OfferDetail
        fields = ['id', 'url']

    def get_url(self, obj):
        return f"http://127.0.0.1:8000/api/offerdetails/{obj.id}/"


class UserDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username']


class OfferListSerializer(serializers.ModelSerializer):
    """
    Serializer for listing offers with summary information.
    Used in list views to provide comprehensive offer data including details,
    pricing information, and user details for paginated responses.
    """
    details = OfferDetailListSerializer(many=True, read_only=True)
    min_price = serializers.SerializerMethodField()
    min_delivery_time = serializers.SerializerMethodField()
    user_details = UserDetailsSerializer(source='user', read_only=True)
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)

    class Meta:
        model = Offer
        fields = [
            'id',
            'user',
            'title',
            'image',
            'description',
            'created_at',
            'updated_at',
            'details',
            'min_price',
            'min_delivery_time',
            'user_details',
        ]

    def get_min_price(self, obj):
        """
        Calculate and return the minimum price from all offer details.
        Returns: Decimal or None if no details exist
        """
        details = obj.details.all()
        return details.aggregate(Min('price'))['price__min'] if details else None

    def get_min_delivery_time(self, obj):
        """
        Calculate and return the minimum delivery time from all offer details.
        Returns: Integer (days) or None if no details exist
        """
        details = obj.details.all()
        return details.aggregate(Min('delivery_time_in_days'))['delivery_time_in_days__min'] if details else None


class OfferDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = OfferDetail
        fields = [
            'id',
            'title',
            'revisions',
            'delivery_time_in_days',
            'price',
            'features',
            'offer_type',
        ]


class OfferRetrieveSerializer(serializers.ModelSerializer):
    """
    Serializer for retrieving individual offers with detailed information.
    Used in detail views to provide complete offer data with absolute URLs
    for offer details and calculated pricing/delivery information.
    """
    details = OfferDetailRetrieveListSerializer(many=True, read_only=True)
    min_price = serializers.SerializerMethodField()
    min_delivery_time = serializers.SerializerMethodField()
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)

    class Meta:
        model = Offer
        fields = [
            'id',
            'user',
            'title',
            'image',
            'description',
            'created_at',
            'updated_at',
            'details',
            'min_price',
            'min_delivery_time',
        ]

    def get_min_price(self, obj):
        """
        Calculate and return the minimum price from all offer details.
        Returns: Decimal or None if no details exist
        """
        details = obj.details.all()
        return details.aggregate(Min('price'))['price__min'] if details else None

    def get_min_delivery_time(self, obj):
        """
        Calculate and return the minimum delivery time from all offer details.
        Returns: Integer (days) or None if no details exist
        """
        details = obj.details.all()
        return details.aggregate(Min('delivery_time_in_days'))['delivery_time_in_days__min'] if details else None


class OfferUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for updating existing offers with partial data support.
    Used in PATCH requests to update offer fields and nested offer details.
    Supports updating individual details by matching their offer_type.
    """
    details = OfferDetailSerializer(many=True, required=False)

    class Meta:
        model = Offer
        fields = [
            'id',
            'title',
            'image',
            'description',
            'details',
        ]

    def update(self, instance, validated_data):
        """
        Update offer instance with validated data including nested details.
        
        Args:
            instance: The existing Offer object to update
            validated_data: Dictionary containing validated field data
            
        Returns:
            Updated Offer instance with modified fields and details
            
        Details are matched by offer_type and updated individually.
        Only provided fields are updated, others remain unchanged.
        """
        details_data = validated_data.pop('details', None)
        
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        if details_data:
            for detail_data in details_data:
                offer_type = detail_data.get('offer_type')
                if offer_type:
                    detail_obj = instance.details.filter(offer_type=offer_type).first()
                    if detail_obj:
                        for key, val in detail_data.items():
                            setattr(detail_obj, key, val)
                        detail_obj.save()
        
        return instance


class OfferSerializer(serializers.ModelSerializer):
    details = OfferDetailSerializer(many=True, read_only=True)

    class Meta:
        model = Offer
        fields = [
            'id',
            'title',
            'image',
            'description',
            'details',
        ]

    def create(self, validated_data):
        return Offer.objects.create(**validated_data)

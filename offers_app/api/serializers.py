from django.contrib.auth.models import User
from rest_framework import serializers
from user_profile.models import Profile
from rest_framework import serializers
from ..models import Offer, OfferDetail
from django.db.models import Min

class OfferDetailListSerializer(serializers.ModelSerializer):
    url = serializers.SerializerMethodField()

    class Meta:
        model = OfferDetail
        fields = [
            'id',
            'url',
        ]

    def get_url(self, obj):
        return f"/offerdetails/{obj.id}/"

class UserDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username']

class OfferListSerializer(serializers.ModelSerializer):
    details = OfferDetailListSerializer(many=True, read_only=True)
    min_price = serializers.SerializerMethodField()
    min_delivery_time = serializers.SerializerMethodField()
    user_details = UserDetailsSerializer(source='user', read_only=True)

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
        details = obj.details.all()
        return details.aggregate(Min('price'))['price__min'] if details else None

    def get_min_delivery_time(self, obj):
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
        # Entferne 'user' aus validated_data, falls vorhanden
        validated_data.pop('user', None)
        return Offer.objects.create(**validated_data)

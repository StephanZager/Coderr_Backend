from django.contrib.auth.models import User
from rest_framework import serializers
from ..models import Offer, OfferDetail
from django.db.models import Min


class OfferDetailListSerializer(serializers.ModelSerializer):
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
    details = OfferDetailListSerializer(many=True, read_only=True)
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
            'user_details',
        ]


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
    details = OfferDetailListSerializer(many=True, read_only=True)
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
        ]


class OfferUpdateSerializer(serializers.ModelSerializer):
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


class OfferSerializer(serializers.ModelSerializer):
    details = OfferDetailSerializer(many=True, read_only=True)

    class Meta:
        model = Offer
        fields = [
            'id',
            'user',
            'title',
            'image',
            'description',
            'details',
        ]


class OfferSerializer(serializers.ModelSerializer):
    details = OfferDetailSerializer(many=True, read_only=True)

    class Meta:
        model = Offer
        fields = [
            'id',
            'user',
            'title',
            'image',
            'description',
            'details',
        ]

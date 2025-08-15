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
        fields = ['id', 'url']
    def get_url(self, obj):
        return f"http://127.0.0.1:8000/api/offerdetails/{obj.id}/"

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

class OfferRetrieveSerializer(serializers.ModelSerializer):
    details = OfferDetailListSerializer(many=True, read_only=True)
    min_price = serializers.SerializerMethodField()
    min_delivery_time = serializers.SerializerMethodField()
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
        details = obj.details.all()
        return details.aggregate(Min('price'))['price__min'] if details else None
    def get_min_delivery_time(self, obj):
        details = obj.details.all()
        return details.aggregate(Min('delivery_time_in_days'))['delivery_time_in_days__min'] if details else None

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
    def update(self, instance, validated_data):
        details_data = validated_data.pop('details', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        if details_data:
            for detail_data in details_data:
                offer_type = detail_data.get('offer_type')
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
            'user',
            'title',
            'image',
            'description',
            'details',
        ]

    def create(self, validated_data):
        return Offer.objects.create(**validated_data)

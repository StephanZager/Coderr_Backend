from rest_framework import serializers
from orders_app.models import Order
from django.contrib.auth.models import User
from offers_app.models import OfferDetail, Offer

class UserDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username']

class OrderSerializer(serializers.ModelSerializer):
    offer_detail_id = serializers.IntegerField(write_only=True)
    customer_user = UserDetailsSerializer(read_only=True)
    business_user = UserDetailsSerializer(read_only=True)

    class Meta:
        model = Order
        fields = [
            'id', 'offer_detail_id', 'customer_user', 'business_user', 'title',
            'revisions', 'delivery_time_in_days', 'price', 'features',
            'offer_type', 'status', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'customer_user', 'business_user', 'title', 'revisions', 'delivery_time_in_days', 'price', 'features', 'offer_type', 'status', 'created_at', 'updated_at']

    def create(self, validated_data):
        offer_detail_id = validated_data.pop('offer_detail_id')
        offer_detail = OfferDetail.objects.get(id=offer_detail_id)
        offer = offer_detail.offer

        customer_user = self.context['request'].user
        business_user = offer.user

        order_data = {
            'customer_user': customer_user,
            'business_user': business_user,
            'title': offer_detail.title,
            'revisions': offer_detail.revisions,
            'delivery_time_in_days': offer_detail.delivery_time_in_days,
            'price': offer_detail.price,
            'features': offer_detail.features,
            'offer_type': offer_detail.offer_type,
        }
        order = Order.objects.create(**order_data)
        return order

class OrderUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ['id', 'status']
        read_only_fields = ['id']

class OrderListSerializer(serializers.ModelSerializer):
    customer_user = UserDetailsSerializer(read_only=True)
    business_user = UserDetailsSerializer(read_only=True)
    
    class Meta:
        model = Order
        fields = [
            'id', 'customer_user', 'business_user', 'title',
            'revisions', 'delivery_time_in_days', 'price', 'features',
            'offer_type', 'status', 'created_at', 'updated_at'
        ]
        read_only_fields = fields
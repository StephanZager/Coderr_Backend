from rest_framework import serializers
from orders_app.models import Order
from django.contrib.auth.models import User
from offers_app.models import OfferDetail, Offer

class UserDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username']

class OrderSerializer(serializers.ModelSerializer):
    """
    Serializer for creating new orders from offer details.
    
    Handles order creation by taking an offer_detail_id and automatically
    populating order fields with data from the associated offer detail.
    Sets customer_user from request context and business_user from offer owner.
    
    Fields:
        offer_detail_id: ID of the offer detail to create order from (write-only)
        customer_user: User who created the order (auto-populated, read-only)
        business_user: User who owns the offer (auto-populated, read-only)
        All other fields: Copied from the selected offer detail
    """
    offer_detail_id = serializers.IntegerField(write_only=True)
    customer_user = serializers.PrimaryKeyRelatedField(read_only=True) 
    business_user = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Order
        fields = [
            'id', 'offer_detail_id', 'customer_user', 'business_user', 'title',
            'revisions', 'delivery_time_in_days', 'price', 'features',
            'offer_type', 'status', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'customer_user', 'business_user', 'title', 'revisions', 'delivery_time_in_days', 'price', 'features', 'offer_type', 'status', 'created_at', 'updated_at']

    def create(self, validated_data):
        """
        Create a new order from an offer detail.
        
        Args:
            validated_data: Dictionary containing offer_detail_id
            
        Returns:
            Order: Newly created order instance with data copied from offer detail
            
        Process:
            1. Extracts offer_detail_id from validated data
            2. Retrieves the corresponding OfferDetail and Offer objects
            3. Sets customer_user from request context (authenticated user)
            4. Sets business_user from offer owner
            5. Copies all relevant fields from offer detail to order
            6. Creates and returns the new order
        """
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
    """
    Serializer for displaying order information in list and detail views.
    
    Provides complete order data with read-only fields for viewing purposes.
    Used for GET requests to display order details to both customer and business users.
    All fields are read-only to ensure data integrity in display contexts.
    
    Fields:
        customer_user: ID of the user who placed the order
        business_user: ID of the user who owns the offer/service
        All other fields: Complete order information including pricing, timeline, and status
    """
    customer_user = serializers.PrimaryKeyRelatedField(read_only=True)
    business_user = serializers.PrimaryKeyRelatedField(read_only=True)
    
    class Meta:
        model = Order
        fields = [
            'id', 'customer_user', 'business_user', 'title',
            'revisions', 'delivery_time_in_days', 'price', 'features',
            'offer_type', 'status', 'created_at', 'updated_at'
        ]
        read_only_fields = fields
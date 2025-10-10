from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.exceptions import NotFound  # <-- Hinzugefügt
from django.shortcuts import get_object_or_404
from django.db.models import Q
from orders_app.models import Order
from offers_app.models import OfferDetail
from user_profile.models import Profile
from .serializers import (
    OrderSerializer,
    OrderUpdateSerializer,
    OrderListSerializer
)
from .permissions import IsCustomerUser, IsBusinessUser

class OrderListView(generics.ListCreateAPIView):
    """
    API view for listing and creating orders.
    
    Provides order management functionality where users can view their orders
    and create new orders from offer details. Filters orders to show only
    those where the user is either customer or business user.
    
    Permissions:
        GET: Authenticated users can view their orders
        POST: Only customer users can create new orders
        
    Queryset: Orders where user is customer_user OR business_user
    """
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        Return orders where the current user is either customer or business user.
        
        Returns:
            QuerySet: Filtered orders for the authenticated user
        """
        user = self.request.user
        return Order.objects.filter(Q(customer_user=user) | Q(business_user=user))

    def get_serializer_class(self):
        """
        Return appropriate serializer based on request method.
        
        Returns:
            Serializer: OrderSerializer for POST, OrderListSerializer for GET
        """
        if self.request.method == 'POST':
            return OrderSerializer
        return OrderListSerializer

    def get_permissions(self):
        """
        Determine permissions based on request method.
        POST requests require customer user authentication.
        
        Returns:
            list: Permission classes for the current request
        """
        if self.request.method == 'POST':
            self.permission_classes = [IsAuthenticated, IsCustomerUser]
        return super().get_permissions()

    def create(self, request, *args, **kwargs):
        """
        Create a new order from an offer detail.
        
        Validates the offer_detail_id, checks if the offer has an associated
        business user, and creates a new order with data from the offer detail.
        
        Args:
            request: HTTP request containing offer_detail_id
            
        Returns:
            Response: Created order data with 201 status
            
        Raises:
            400: Invalid offer_detail_id or missing business user
            404: Offer detail not found
        """
        offer_detail_id = request.data.get('offer_detail_id')
        if not offer_detail_id:
            return Response({"error": "Invalid request data. 'offer_detail_id'."}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            offer_detail_id = int(offer_detail_id)
        except (ValueError, TypeError):
             return Response(
                 {"error": "Invalid offer_detail_id format. Must be a number."}, 
                 status=status.HTTP_400_BAD_REQUEST
            )

        try:
            offer_detail = OfferDetail.objects.get(id=offer_detail_id)
        except OfferDetail.DoesNotExist:
            raise NotFound(detail="The specified offer detail was not found.")

        if not offer_detail.offer.user:
            return Response({"error": "The offer has no associated business user."}, status=status.HTTP_400_BAD_REQUEST)

        serializer = self.get_serializer(data={'offer_detail_id': offer_detail_id})
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

class OrderDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    API view for retrieving, updating, and deleting individual orders.
    
    Provides detailed order management with different permissions based on
    the HTTP method. Supports full order retrieval, status updates by business
    users, and deletion by admin users only.
    
    Permissions:
        GET: Any authenticated user can view order details
        PATCH/PUT: Only business users can update order status
        DELETE: Only admin users can delete orders
        
    Serializers:
        GET: OrderListSerializer (complete order data)
        PATCH/PUT: OrderUpdateSerializer (status updates only)
    """
    queryset = Order.objects.all()
    
    def get_serializer_class(self):
        """
        Return appropriate serializer based on request method.
        
        Returns:
            Serializer: OrderUpdateSerializer for updates, OrderListSerializer for retrieval
        """
        if self.request.method in ['PATCH', 'PUT']:
            return OrderUpdateSerializer
        return OrderListSerializer

    def get_permissions(self):
        """
        Determine permissions based on request method.
        
        Returns:
            list: Permission classes for the current request
            
        Permission Matrix:
            - DELETE: Admin users only
            - PATCH/PUT: Authenticated business users
            - GET: Any authenticated user
        """
        if self.request.method == 'DELETE':
            self.permission_classes = [IsAdminUser]
        elif self.request.method in ['PATCH', 'PUT']:
            self.permission_classes = [IsAuthenticated, IsBusinessUser]
        else:
            self.permission_classes = [IsAuthenticated]
        return super().get_permissions()

    def get_object(self):
        """
        Retrieve and return the order object with permission checks.
        
        Returns:
            Order: The requested order instance
            
        Raises:
            404: If order not found
            403: If user lacks object-level permissions
        """
        obj = get_object_or_404(self.get_queryset(), pk=self.kwargs['pk'])
        self.check_object_permissions(self.request, obj)
        return obj

    def update(self, request, *args, **kwargs):
        """
        Update order status and return complete order data.
        
        Uses OrderUpdateSerializer for validation but returns complete order
        data using OrderListSerializer to match API documentation requirements.
        
        Args:
            request: HTTP request containing status update data
            
        Returns:
            Response: Complete updated order data with all fields
        """
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        
        full_serializer = OrderListSerializer(instance)
        return Response(full_serializer.data)

    def destroy(self, request, *args, **kwargs):
        """
        Delete the specified order.
        
        Args:
            request: HTTP delete request
            
        Returns:
            Response: Empty response with 204 status code
        """
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)

class OrderCountView(generics.RetrieveAPIView):
    """
    API view for retrieving the count of in-progress orders for a business user.
    
    Provides a simple endpoint to get the number of orders with 'in_progress'
    status for a specific business user. Used for dashboard statistics and
    business user profile information.
    
    Permissions:
        GET: Any authenticated user can view order counts
        
    URL Parameters:
        business_user_id: ID of the business user to count orders for
        
    Response Format:
        {"order_count": integer}
    """
    permission_classes = [IsAuthenticated]

    def get_object(self):
        """
        Calculate and return in-progress order count for specified business user.
        
        Returns:
            dict: Dictionary containing order_count for the business user
            
        Raises:
            404: If no business user found with the specified ID
            
        Process:
            1. Extract business_user_id from URL parameters
            2. Validate that user exists and has business profile type
            3. Count orders with status 'in_progress' for that user
            4. Return count as dictionary
        """
        user_id = self.kwargs['business_user_id']
        try:
            user = Profile.objects.get(user__id=user_id, type='business').user
        except Profile.DoesNotExist:
            raise NotFound("No business user found with the specified ID.")
        
        order_count = Order.objects.filter(business_user=user, status='in_progress').count()
        return {'order_count': order_count}
    
    def retrieve(self, request, *args, **kwargs):
        """
        Handle GET request to retrieve order count.
        
        Args:
            request: HTTP GET request
            
        Returns:
            Response: JSON response with order count and 200 status
        """
        instance = self.get_object()
        return Response(instance, status=status.HTTP_200_OK)

class CompletedOrderCountView(generics.RetrieveAPIView):
    """
    API view for retrieving the count of completed orders for a business user.
    
    Provides a simple endpoint to get the number of orders with 'completed'
    status for a specific business user. Used for dashboard statistics and
    business user profile information to show successful project completions.
    
    Permissions:
        GET: Any authenticated user can view completed order counts
        
    URL Parameters:
        business_user_id: ID of the business user to count completed orders for
        
    Response Format:
        {"completed_order_count": integer}
    """
    permission_classes = [IsAuthenticated]

    def get_object(self):
        """
        Calculate and return completed order count for specified business user.
        
        Returns:
            dict: Dictionary containing completed_order_count for the business user
            
        Raises:
            404: If no business user found with the specified ID
            
        Process:
            1. Extract business_user_id from URL parameters
            2. Validate that user exists and has business profile type
            3. Count orders with status 'completed' for that user
            4. Return count as dictionary
        """
        user_id = self.kwargs['business_user_id']
        try:
            user = Profile.objects.get(user__id=user_id, type='business').user
        except Profile.DoesNotExist:
            raise NotFound("No business user found with the specified ID.")
        
        completed_order_count = Order.objects.filter(business_user=user, status='completed').count()
        return {'completed_order_count': completed_order_count}

    def retrieve(self, request, *args, **kwargs):
        """
        Handle GET request to retrieve completed order count.
        
        Args:
            request: HTTP GET request
            
        Returns:
            Response: JSON response with completed order count and 200 status
        """
        instance = self.get_object()
        return Response(instance, status=status.HTTP_200_OK)
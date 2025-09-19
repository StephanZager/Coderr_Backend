from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
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
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Order.objects.filter(Q(customer_user=user) | Q(business_user=user))

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return OrderSerializer
        return OrderListSerializer

    def get_permissions(self):
        if self.request.method == 'POST':
            self.permission_classes = [IsAuthenticated, IsCustomerUser]
        return super().get_permissions()

    def create(self, request, *args, **kwargs):
        offer_detail_id = request.data.get('offer_detail_id')
        if not offer_detail_id:
            return Response({"error": "Ungültige Anfragedaten. 'offer_detail_id' fehlt."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            offer_detail = OfferDetail.objects.get(id=offer_detail_id)
        except OfferDetail.DoesNotExist:
            return Response({"error": "Das angegebene Angebotsdetail wurde nicht gefunden."}, status=status.HTTP_404_NOT_FOUND)

        if not offer_detail.offer.user:
            return Response({"error": "Das Angebot hat keinen zugehörigen Business-Nutzer."}, status=status.HTTP_400_BAD_REQUEST)

        serializer = self.get_serializer(data={'offer_detail_id': offer_detail_id})
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

class OrderDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Order.objects.all()
    
    def get_serializer_class(self):
        if self.request.method in ['PATCH', 'PUT']:
            return OrderUpdateSerializer
        return OrderListSerializer

    def get_permissions(self):
        if self.request.method == 'DELETE':
            self.permission_classes = [IsAdminUser]
        elif self.request.method in ['PATCH', 'PUT']:
            self.permission_classes = [IsAuthenticated, IsBusinessUser]
        else:
            self.permission_classes = [IsAuthenticated]
        return super().get_permissions()

    def get_object(self):
        obj = get_object_or_404(self.get_queryset(), pk=self.kwargs['pk'])
        self.check_object_permissions(self.request, obj)
        return obj

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)

class OrderCountView(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated]

    def get_object(self):
        user_id = self.kwargs['business_user_id']
        try:
            user = Profile.objects.get(user__id=user_id, type='business').user
        except Profile.DoesNotExist:
            raise status.HTTP_404_NOT_FOUND("Kein Geschäftsnutzer mit der angegebenen ID gefunden.")
        
        order_count = Order.objects.filter(business_user=user, status='in_progress').count()
        return {'order_count': order_count}
    
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        return Response(instance, status=status.HTTP_200_OK)

class CompletedOrderCountView(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated]

    def get_object(self):
        user_id = self.kwargs['business_user_id']
        try:
            user = Profile.objects.get(user__id=user_id, type='business').user
        except Profile.DoesNotExist:
            raise status.HTTP_404_NOT_FOUND("Kein Geschäftsnutzer mit der angegebenen ID gefunden.")
        
        completed_order_count = Order.objects.filter(business_user=user, status='completed').count()
        return {'completed_order_count': completed_order_count}

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        return Response(instance, status=status.HTTP_200_OK)
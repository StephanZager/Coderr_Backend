from django.shortcuts import get_object_or_404
from rest_framework import generics, filters, status
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from django.db.models import Min
from .serializers import (
    OfferDetailSerializer, OfferSerializer, OfferListSerializer,
    OfferRetrieveSerializer, OfferUpdateSerializer
)
from ..models import Offer, OfferDetail
from django.contrib.auth.models import User
from rest_framework.permissions import IsAuthenticated
from .permissions import IsBusinessUser, IsOwner

class OfferPagination(PageNumberPagination):
    page_size_query_param = 'page_size'

class OfferView(generics.ListCreateAPIView):
    queryset = Offer.objects.all()
    pagination_class = OfferPagination
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'description']
    ordering_fields = ['updated_at', 'min_price']

    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsBusinessUser()]
        return []

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return OfferListSerializer
        return OfferSerializer

    def get_queryset(self):
        qs = Offer.objects.all()
        creator_id = self.request.query_params.get('creator_id')
        min_price = self.request.query_params.get('min_price')
        max_delivery_time = self.request.query_params.get('max_delivery_time')
        ordering = self.request.query_params.get('ordering')

        if creator_id:
            qs = qs.filter(user_id=creator_id)
        if min_price:
            qs = qs.filter(details__price__gte=min_price)
        if max_delivery_time:
            qs = qs.filter(details__delivery_time_in_days__lte=max_delivery_time)
        if ordering:
            qs = qs.order_by(ordering)
        return qs.distinct()

    def create(self, request, *args, **kwargs):
        data = request.data
        details_data = data.get('details', [])
        if len(details_data) != 3:
            return Response({"error": "Ein Angebot muss genau 3 Details enthalten."}, status=status.HTTP_400_BAD_REQUEST)
        offer_serializer = OfferSerializer(data=data)
        offer_serializer.is_valid(raise_exception=True)
        offer = offer_serializer.save(user=request.user)
        for detail in details_data:
            OfferDetail.objects.create(offer=offer, **detail)
        response_serializer = OfferSerializer(offer)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        page = self.paginate_queryset(queryset)
        results = []
        offers = page if page is not None else queryset
        for offer in offers:
            details = offer.details.all()
            min_price = details.aggregate(Min('price'))['price__min'] if details else None
            min_delivery_time = details.aggregate(Min('delivery_time_in_days'))['delivery_time_in_days__min'] if details else None
            user = offer.user if hasattr(offer, 'user') and offer.user is not None else None
            user_details = {
                "first_name": user.first_name if user else "",
                "last_name": user.last_name if user else "",
                "username": user.username if user else "",
            }
            created_at = offer.created_at if hasattr(offer, 'created_at') else None
            updated_at = offer.updated_at if hasattr(offer, 'updated_at') else None
            results.append({
                "id": offer.id,
                "user": user.id if user else None,
                "title": offer.title,
                "image": offer.image.url if offer.image else None,
                "description": offer.description,
                "created_at": created_at,
                "updated_at": updated_at,
                "details": [{"id": d.id, "url": f"/offerdetails/{d.id}/"} for d in details],
                "min_price": min_price,
                "min_delivery_time": min_delivery_time,
                "user_details": user_details,
            })
        if page is not None:
            return self.get_paginated_response(results)
        return Response(results)

class OfferDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Offer.objects.all()
    permission_classes = [IsAuthenticated, IsOwner]

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return OfferRetrieveSerializer
        if self.request.method in ['PATCH', 'PUT']:
            return OfferUpdateSerializer
        return OfferRetrieveSerializer

class OfferDetailObjView(generics.RetrieveAPIView):
    queryset = OfferDetail.objects.all()
    serializer_class = OfferDetailSerializer
    permission_classes = [IsAuthenticated]
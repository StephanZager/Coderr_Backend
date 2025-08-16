from django.shortcuts import get_object_or_404
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from .serializers import (
    OfferDetailSerializer, OfferSerializer, OfferListSerializer,
    OfferRetrieveSerializer, OfferUpdateSerializer
)
from ..models import Offer, OfferDetail
from rest_framework.permissions import IsAuthenticated
from .permissions import IsBusinessUser, IsOwner


class OfferPagination(PageNumberPagination):
    page_size_query_param = 'page_size'


class OfferView(generics.ListCreateAPIView):
    queryset = Offer.objects.all()
    pagination_class = OfferPagination

    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsBusinessUser()]
        return []

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return OfferListSerializer
        return OfferSerializer

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
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


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

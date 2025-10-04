
from django.shortcuts import get_object_or_404
from rest_framework import generics, status, filters
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from .serializers import (
    OfferDetailSerializer, OfferSerializer, OfferListSerializer,
    OfferRetrieveSerializer, OfferUpdateSerializer
)
from ..models import Offer, OfferDetail
from ..filters import OfferFilter
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from .permissions import IsBusinessUser, IsOwner
from django_filters.rest_framework import DjangoFilterBackend, Filter


class OfferPagination(PageNumberPagination):
    """
    Custom pagination class for offer listings.
    
    Provides paginated responses with configurable page sizes.
    Default page size is 5 items per page, with user-configurable
    page_size parameter up to a maximum of 100 items per page.
    
    Query Parameters:
        page_size: Number of results per page (max 100)
        page: Page number to retrieve
    """
    page_size = 5
    page_size_query_param = 'page_size'
    max_page_size = 100


class OfferView(generics.ListCreateAPIView):
    """
    API view for listing and creating offers.
    
    Provides comprehensive offer management with filtering, searching,
    ordering, and pagination capabilities. Supports creating new offers
    with exactly 3 detail packages (basic, standard, premium).
    
    Permissions:
        GET: Any authenticated user or read-only access
        POST: Only business users can create offers
        
    Filtering:
        - creator_id: Filter by offer creator
        - min_price: Minimum price filter
        - max_delivery_time: Maximum delivery time filter
        
    Search: title, description fields
    Ordering: updated_at, price fields
    Pagination: 5 items per page (configurable)
    """
    queryset = Offer.objects.all()
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter
    ]
    filterset_class = OfferFilter
    search_fields = ['title', 'description']
    ordering_fields = ['updated_at', 'price']
    pagination_class = OfferPagination

    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsBusinessUser()]
        return [IsAuthenticatedOrReadOnly()]

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return OfferListSerializer
        return OfferSerializer

    def create(self, request, *args, **kwargs):
        """
        Create a new offer with exactly 3 detail packages.
        
        Validates that exactly 3 details are provided and creates
        the offer with associated detail objects.
        
        Returns:
            Response: Created offer data with 201 status
            
        Raises:
            400: If not exactly 3 details provided
        """
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


class OfferDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Offer.objects.all()

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return OfferRetrieveSerializer
        if self.request.method in ['PATCH', 'PUT']:
            return OfferUpdateSerializer
        return OfferRetrieveSerializer
    
    def get_permissions(self):
        if self.request.method in ['PATCH', 'PUT', 'DELETE']:
            return [IsAuthenticated(), IsOwner()]
        return [IsAuthenticated()]

class OfferDetailObjView(generics.RetrieveAPIView):
    queryset = OfferDetail.objects.all()
    serializer_class = OfferDetailSerializer
    permission_classes = [IsAuthenticated]

from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.filters import OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from ..models import Review
from .serializers import ReviewSerializer
from .permissions import IsReviewer, IsCustomerUser
from django.db.models import F

class ReviewListView(generics.ListCreateAPIView):
    """
    API view for listing and creating reviews.
    
    Provides filtering by business_user/reviewer and ordering by updated_at/rating.
    Only customer users can create reviews, all authenticated users can view.
    
    Permissions:
        GET: Authenticated users
        POST: Customer users only
        
    Filters: business_user, reviewer (exact match)
    Ordering: updated_at, rating (default: -updated_at)
    """
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = {
        'business_user': ['exact'],
        'reviewer': ['exact'],
    }
    ordering_fields = ['updated_at', 'rating']

    def get_permissions(self):
        """
        Return appropriate permissions based on request method.
        POST requires customer user, GET requires authentication only.
        """
        if self.request.method == 'POST':
            return [IsAuthenticated(), IsCustomerUser()]
        return [IsAuthenticated()]

    def get_queryset(self):
        """
        Return ordered queryset with default ordering by -updated_at.
        Validates ordering parameter against allowed fields.
        """
        queryset = super().get_queryset()
        ordering = self.request.query_params.get('ordering', '-updated_at')
        if ordering not in self.ordering_fields:
            ordering = '-updated_at'
        return queryset.order_by(ordering)

class ReviewDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    API view for retrieving, updating, and deleting individual reviews.
    
    Only the review creator can perform update/delete operations.
    Supports partial updates for rating and description fields only.
    
    Permissions: Authenticated users who own the review
    """
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticated, IsReviewer]
    
    def update(self, request, *args, **kwargs):
        """
        Update review with rating and description only.
        Preserves existing values if not provided in request.
        """
        instance = self.get_object()
        data = {
            'rating': request.data.get('rating', instance.rating),
            'description': request.data.get('description', instance.description)
        }
        serializer = self.get_serializer(instance, data=data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def delete(self, request, *args, **kwargs):
        """
        Delete the review and return 204 No Content.
        """
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)
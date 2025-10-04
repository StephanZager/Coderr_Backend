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
        if self.request.method == 'POST':
            return [IsAuthenticated(), IsCustomerUser()]
        return [IsAuthenticated()]

    def get_queryset(self):
        queryset = super().get_queryset()
        # Verwende F-Ausdrücke, um die Sortierreihenfolge umzukehren, falls 'ordering' nicht angegeben ist
        ordering = self.request.query_params.get('ordering', '-updated_at')
        if ordering not in self.ordering_fields:
            ordering = '-updated_at'
        return queryset.order_by(ordering)

class ReviewDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticated, IsReviewer]
    
    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        # Nur 'rating' und 'description' sind aktualisierbar
        data = {
            'rating': request.data.get('rating', instance.rating),
            'description': request.data.get('description', instance.description)
        }
        serializer = self.get_serializer(instance, data=data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def delete(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)
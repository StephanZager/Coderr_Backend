from django.urls import path
from .views import OfferView, OfferDetailView, OfferDetailObjView

urlpatterns = [
    path('offers/', OfferView.as_view(), name='offer-list'),  # GET, POST
    path('offers/<int:pk>/', OfferDetailView.as_view(), name='offer-detail'),  # GET, PATCH, DELETE
    path('offerdetails/<int:pk>/', OfferDetailObjView.as_view(), name='offerdetail-detail'),  # GET
]
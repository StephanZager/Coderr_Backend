from django.db import models
from django.contrib.auth.models import User
from offers_app.models import OfferDetail, Offer

class Order(models.Model):
    STATUS_CHOICES = [
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]

    customer_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='customer_orders', null=True, blank=True)
    business_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='business_orders', null=True, blank=True)
    title = models.CharField(max_length=50)
    revisions = models.IntegerField()
    delivery_time_in_days = models.IntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    features = models.JSONField(blank=True, default=list)
    offer_type = models.CharField(max_length=20)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='in_progress')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title
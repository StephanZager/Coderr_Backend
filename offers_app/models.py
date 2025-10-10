from django.db import models
from django.contrib.auth.models import User
from django.contrib import admin

class Offer(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='offers', null=True, blank=True)
    title = models.CharField(max_length=255, default='', blank=True)
    image = models.ImageField(upload_to='offer_images/', null=True, blank=True)
    description = models.TextField(max_length=255, default='', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class OfferDetail(models.Model):
    offer = models.ForeignKey(Offer, related_name='details', on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    revisions = models.IntegerField()
    delivery_time_in_days = models.IntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    features = models.JSONField(default=list, blank=True) 
    offer_type = models.CharField(max_length=20)

admin.site.register(Offer)
admin.site.register(OfferDetail)
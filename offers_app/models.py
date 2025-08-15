from django.db import models
from django.contrib.auth.models import User

class Offer(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='offers', null=True, blank=True)
    title = models.CharField(max_length=25, default='', blank=True)
    image = models.ImageField(upload_to='offer_images/', null=True, blank=True)
    description = models.TextField(max_length=255, default='', blank=True)

class OfferDetail(models.Model):
    offer = models.ForeignKey(Offer, related_name='details', on_delete=models.CASCADE)
    title = models.CharField(max_length=50)
    revisions = models.IntegerField()
    delivery_time_in_days = models.IntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    features = models.JSONField(default=list, blank=True) 
    offer_type = models.CharField(max_length=20)
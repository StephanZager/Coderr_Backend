from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Profile(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    type = models.CharField(max_length=20, choices=[('customer', 'Customer'), ('business', 'Business')], default='customer')
    #file = models.ImageField(upload_to='profile_pics/', null=True, blank=True) 
    location = models.CharField(max_length=25, default='', blank=True)
    tel = models.CharField(max_length=15, default='', blank=True)
    description= models.TextField(max_length=255, default='', blank=True)
    working_hours = models.CharField(max_length=20, default='', blank=True)

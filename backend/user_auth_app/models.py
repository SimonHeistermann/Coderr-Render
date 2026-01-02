from django.db import models
from django.contrib.auth.models import User


class UserProfile(models.Model):
    CUSTOMER = 'customer'
    BUSINESS = 'business'
    USERTYPE_CHOICES = [(CUSTOMER, 'customer'), (BUSINESS, 'business')]

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    type = models.CharField(max_length=10, choices=USERTYPE_CHOICES, default=CUSTOMER, db_index=True)

    file = models.FileField(upload_to='avatars/', blank=True, null=True)
    location = models.CharField(default='', max_length=255, blank=True, null=True)
    tel = models.CharField(default='', max_length=100, blank=True, null=True)
    description = models.TextField(default='', blank=True, null=True)
    working_hours = models.CharField(default='', max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user.username} ({self.type})"
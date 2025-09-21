from django.db import models
from django.contrib.auth.models import User

class Review(models.Model):
    business_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_reviews')
    reviewer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='given_reviews')
    rating = models.IntegerField()
    description = models.TextField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        # Ein Benutzer kann ein Geschäft nur einmal bewerten
        unique_together = ('business_user', 'reviewer',)

    def __str__(self):
        return f"Review for {self.business_user.username} by {self.reviewer.username}"

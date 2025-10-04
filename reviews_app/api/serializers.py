from rest_framework import serializers
from ..models import Review
from django.contrib.auth.models import User
from django.db.models import F

class ReviewSerializer(serializers.ModelSerializer):
    """
    Serializer for creating and managing reviews.
    
    Handles review creation with duplicate prevention - ensures one review
    per customer-business user pair. Auto-assigns reviewer from request context.
    """
    business_user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    reviewer = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Review
        fields = ['id', 'business_user', 'reviewer', 'rating', 'description', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']

    def create(self, validated_data):
        """
        Create review with duplicate check.
        
        Returns:
            Review: Created review instance
            
        Raises:
            ValidationError: If reviewer already reviewed this business user
        """
        reviewer = self.context['request'].user
        business_user = validated_data.get('business_user')

        if Review.objects.filter(reviewer=reviewer, business_user=business_user).exists():
            raise serializers.ValidationError("You have already left a review for this business user.")

        validated_data['reviewer'] = reviewer
        return super().create(validated_data)
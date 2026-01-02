from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator
from user_auth_app.models import UserProfile


class Offer(models.Model):
    """
    Represents an offer made by business user
    """
    user_profile = models.ForeignKey(UserProfile, related_name='offers', on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    image = models.FileField(upload_to='offers/', null=True, blank=True)
    description = models.TextField(default='', blank=True)
    created_at = models.DateTimeField(auto_now_add=True) 
    updated_at = models.DateTimeField(auto_now=True)    

    def __str__(self):
        return self.title


class OfferDetail(models.Model):
    """
    Represents a offer with different types
    """

    class Meta:
        unique_together = ('offer', 'offer_type')

    BASIC = 'basic'
    STANDARD = 'standard'
    PREMIUM = 'premium'
    OFFER_TYPES = [(BASIC, 'basic'), (STANDARD, 'standard'), (PREMIUM, 'premium')]

    offer = models.ForeignKey(Offer, related_name='details', on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    revisions = models.IntegerField(validators=[MinValueValidator(-1)])
    delivery_time_in_days = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    features = models.JSONField(default=list, blank=True) 
    offer_type = models.CharField(max_length=10, choices=OFFER_TYPES, default=BASIC)

    def __str__(self):
        return f"{self.offer.title} - {self.offer_type}"


class Order(models.Model):
    """
    Represents an order placed by a customer on an orderdetail
    """

    class Status(models.TextChoices):
        IN_PROGRESS = 'in_progress', 'In Progress'
        COMPLETED = 'completed', 'Completed'
        CANCELLED = 'cancelled', 'Cancelled'

    customer_user = models.ForeignKey(UserProfile, related_name='orders', on_delete=models.CASCADE)
    offer_detail = models.ForeignKey(OfferDetail, related_name='orders', on_delete=models.CASCADE)

    status = models.CharField(max_length=35, choices=Status.choices, default=Status.IN_PROGRESS)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Order #{self.id} ({self.status}) - OfferDetail #{self.offer_detail_id}"


class Review(models.Model):
    """
    Represents a review written by a customer for a business user.
    """

    business_user = models.ForeignKey(
        UserProfile,
        related_name="received_reviews",
        on_delete=models.CASCADE,
    )
    reviewer = models.ForeignKey(
        UserProfile,
        related_name="written_reviews",
        on_delete=models.CASCADE,
    )
    rating = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["business_user", "reviewer"],
                name="unique_review_per_business_and_reviewer",
            )
        ]
        ordering = ["-created_at"]
        verbose_name = "Review"
        verbose_name_plural = "Reviews"

    def __str__(self):
        return f"Review by {self.reviewer.user.username} for {self.business_user.user.username}"
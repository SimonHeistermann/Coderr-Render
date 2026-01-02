from django.contrib import admin
from .models import Offer, OfferDetail, Order, Review


@admin.register(Offer)
class OfferAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'description', 'username', 'created_at', 'updated_at']

    def username(self, obj):
        """
        Display the username associated with the offer via the user_profile.
        Assumes Offer has a foreign key to UserProfile, which has a foreign key to User.
        """
        return obj.user_profile.user.username


@admin.register(OfferDetail)
class OfferDetailAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'offer_name']

    def offer_name(self, obj):
        """
        Display the title of the related offer.
        """
        return obj.offer.title


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'offer_provider']
    readonly_fields = ['offer_provider']

    def offer_provider(self, obj):
        """
        Display the user profile associated with the offer provider.
        Accesses Order → OfferDetail → Offer → UserProfile.
        """
        return obj.offer_detail.offer.user_profile


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['id']
import django_filters
from django_filters.rest_framework import FilterSet

from sales_app.models import Offer


class OfferFilter(FilterSet):
    """
    FilterSet for filtering Offer objects.

    Query params:
    - creator_id: filters by offer.user_profile_id
    - max_delivery_time: filters by annotated min_delivery_time <= value
    - min_price: filters by annotated min_price >= value
    """

    creator_id = django_filters.NumberFilter(field_name="user_profile_id")
    max_delivery_time = django_filters.NumberFilter(method="filter_max_delivery_time")
    min_price = django_filters.NumberFilter(method="filter_min_price")

    class Meta:
        model = Offer
        fields = []

    def filter_max_delivery_time(self, qs, name, value):
        return qs.filter(min_delivery_time__lte=value)

    def filter_min_price(self, qs, name, value):
        return qs.filter(min_price__gte=value)
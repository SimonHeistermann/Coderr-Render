from django.db import IntegrityError
from rest_framework import serializers
from rest_framework.exceptions import NotFound, PermissionDenied, ValidationError
from rest_framework.serializers import HyperlinkedModelSerializer, ModelSerializer

from sales_app.models import Offer, OfferDetail, Order, Review


class StrictModelSerializer(serializers.ModelSerializer):
    """
    Reject unexpected input fields.
    """

    def to_internal_value(self, data):
        allowed = set(self.fields.keys())
        received = set(data.keys())
        unexpected = received - allowed
        if unexpected:
            raise serializers.ValidationError(
                {"non_field_errors": f"Unexpected fields: {', '.join(unexpected)}"}
            )
        return super().to_internal_value(data)


class OfferDetailUrlSerializer(HyperlinkedModelSerializer):
    class Meta:
        model = OfferDetail
        fields = [
            "id",
            "url",
            "title",
            "revisions",
            "delivery_time_in_days",
            "price",
            "features",
            "offer_type",
        ]
        extra_kwargs = {"url": {"view_name": "offer-detail-detail"}}


class OfferDetailSerializer(ModelSerializer):
    def validate_revisions(self, value):
        if value != -1 and value < 0:
            raise serializers.ValidationError("Revisions must be -1 (unlimited) or >= 0.")
        return value
    class Meta:
        model = OfferDetail
        fields = [
            "id",
            "title",
            "revisions",
            "delivery_time_in_days",
            "price",
            "features",
            "offer_type",
        ]
        read_only_fields = ["id"]


class OfferDetailLightSerializer(HyperlinkedModelSerializer):
    """
    Light representation used for offer list/detail pages:
    details: [{id, url}]
    """
    class Meta:
        model = OfferDetail
        fields = ["id", "url"]
        extra_kwargs = {"url": {"view_name": "offer-detail-detail"}}


class OfferBaseSerializer(ModelSerializer):
    user = serializers.SerializerMethodField()
    user_details = serializers.SerializerMethodField()
    min_price = serializers.SerializerMethodField()
    min_delivery_time = serializers.SerializerMethodField()

    class Meta:
        model = Offer
        fields = [
            "id",
            "title",
            "image",
            "description",
            "details",
            "created_at",
            "updated_at",
            "user",
            "user_details",
            "min_price",
            "min_delivery_time",
        ]
        extra_kwargs = {
            "created_at": {"read_only": True},
            "updated_at": {"read_only": True},
        }

    def get_min_price(self, obj):
        annotated = getattr(obj, "min_price", None)
        if annotated is not None:
            return annotated
        prices = obj.details.values_list("price", flat=True)
        return min(prices) if prices else None

    def get_min_delivery_time(self, obj):
        annotated = getattr(obj, "min_delivery_time", None)
        if annotated is not None:
            return annotated
        times = obj.details.values_list("delivery_time_in_days", flat=True)
        return min(times) if times else None

    def get_user(self, obj):
        return obj.user_profile.id

    def get_user_details(self, obj):
        user = obj.user_profile.user
        return {
            "first_name": user.first_name,
            "last_name": user.last_name,
            "username": user.username,
        }


class OfferReadSerializer(OfferBaseSerializer):
    """
    Full read serializer (if you ever want it): includes more detail fields.
    Currently not used for list/detail because frontend expects light details.
    """
    details = OfferDetailUrlSerializer(many=True)


class OfferListSerializer(OfferBaseSerializer):
    """
    Public list/detail representation for frontend:
    details only as [{id, url}]
    """
    details = OfferDetailLightSerializer(many=True, read_only=True)


class OfferWriteResponseSerializer(OfferBaseSerializer):
    """
    Response serializer after create/update:
    details without url (frontend expectation based on your previous mutation).
    """
    details = OfferDetailSerializer(many=True, read_only=True)


class OfferCreateSerializer(OfferBaseSerializer):
    """
    Write serializer: accepts nested details WITHOUT 'offer' field.
    """
    details = OfferDetailSerializer(many=True)

    def create(self, validated_data):
        request = self.context.get("request")
        user = getattr(request, "user", None)
        user_profile = getattr(user, "userprofile", None)
        if not user_profile:
            raise serializers.ValidationError("User Profile does not exist.")

        details = validated_data.pop("details", [])
        offer = Offer.objects.create(user_profile=user_profile, **validated_data)

        for detail in details:
            try:
                OfferDetail.objects.create(offer=offer, **detail)
            except IntegrityError:
                raise serializers.ValidationError({"detail": "Create Detail failed."})

        return offer

    def update(self, instance, validated_data):
        details_data = validated_data.pop("details", None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if details_data is not None:
            existing_details = {d.offer_type: d for d in instance.details.all()}

            for detail_data in details_data:
                offer_type = detail_data.get("offer_type")

                if offer_type in existing_details:
                    detail = existing_details[offer_type]
                    for attr, value in detail_data.items():
                        setattr(detail, attr, value)
                    detail.save()
                else:
                    try:
                        OfferDetail.objects.create(offer=instance, **detail_data)
                    except IntegrityError:
                        raise serializers.ValidationError({"detail": "Create Detail failed."})

        return instance


class OrderSerializer(StrictModelSerializer):
    offer_detail_id = serializers.IntegerField(write_only=True)

    revisions = serializers.SerializerMethodField()
    delivery_time_in_days = serializers.SerializerMethodField()
    price = serializers.SerializerMethodField()
    features = serializers.SerializerMethodField()
    offer_type = serializers.SerializerMethodField()
    title = serializers.SerializerMethodField()
    business_user = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = [
            "id",
            "title",
            "customer_user",
            "business_user",
            "status",
            "created_at",
            "updated_at",
            "offer_detail_id",
            "revisions",
            "price",
            "delivery_time_in_days",
            "features",
            "offer_type",
        ]
        read_only_fields = ["id", "customer_user", "created_at", "updated_at"]

    def create(self, validated_data):
        request = self.context.get("request")
        user = getattr(request, "user", None)
        profile = getattr(user, "userprofile", None)

        if not profile:
            raise PermissionDenied("User profile not found.")

        offer_detail_id = validated_data.pop("offer_detail_id")

        try:
            detail = OfferDetail.objects.select_related("offer").get(id=offer_detail_id)
        except OfferDetail.DoesNotExist:
            raise NotFound(detail="OfferDetail not found.")

        if profile.type == "business" and detail.offer.user_profile_id == profile.id:
            raise PermissionDenied("You cannot order your own offer.")

        return Order.objects.create(customer_user=profile, offer_detail=detail)

    def get_revisions(self, obj):
        return obj.offer_detail.revisions

    def get_title(self, obj):
        return obj.offer_detail.title

    def get_price(self, obj):
        return obj.offer_detail.price

    def get_delivery_time_in_days(self, obj):
        return obj.offer_detail.delivery_time_in_days

    def get_features(self, obj):
        return obj.offer_detail.features

    def get_offer_type(self, obj):
        return obj.offer_detail.offer_type

    def get_business_user(self, obj):
        return obj.offer_detail.offer.user_profile.id


class ReviewSerializer(serializers.ModelSerializer):
    reviewer = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Review
        fields = [
            "id",
            "business_user",
            "reviewer",
            "rating",
            "description",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "reviewer", "created_at", "updated_at"]

    def create(self, validated_data):
        request = self.context.get("request")
        if not request or not request.user or not request.user.is_authenticated:
            raise PermissionDenied("Authentication required.")

        user_profile = getattr(request.user, "userprofile", None)
        if not user_profile:
            raise PermissionDenied("User profile not found.")

        business_user = validated_data.get("business_user")

        if Review.objects.filter(business_user=business_user, reviewer=user_profile).exists():
            raise serializers.ValidationError(
                {"detail": "You have already submitted a review for this business user."}
            )

        return Review.objects.create(reviewer=user_profile, **validated_data)
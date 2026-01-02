from django.db.models import Avg, Min
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, generics, status
from rest_framework.exceptions import NotFound, PermissionDenied
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import AllowAny, IsAuthenticated, SAFE_METHODS
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.throttling import ScopedRateThrottle

from sales_app.models import Offer, OfferDetail, Order, Review, UserProfile
from .filters import OfferFilter
from .permissions import (
    IsReviewerSelf,
    IsStaffForDeleteOrOrderPartyForReadAndBusinessOwnerForWrite,
    IsUserWithProfile,
    PublicReadBusinessWrite,
    IsBusinessOwnerOrReadOnly,
)
from .serializers import (
    OfferCreateSerializer,
    OfferDetailSerializer,
    OfferListSerializer,
    OfferWriteResponseSerializer,
    OrderSerializer,
    ReviewSerializer,
)


class LargeResultsSetPagination(PageNumberPagination):
    page_size = 6
    page_size_query_param = "page_size"
    max_page_size = 100


class OfferListCreateView(generics.ListCreateAPIView):
    """
    Public browsing (GET) for landing page.
    Only business users can create offers (POST).
    """
    permission_classes = [PublicReadBusinessWrite]
    pagination_class = LargeResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = OfferFilter
    search_fields = ["title", "description"]
    ordering_fields = ["updated_at", "min_price"]
    ordering = ["updated_at"]

    def get_queryset(self):
        return Offer.objects.annotate(
            min_price=Min("details__price"),
            min_delivery_time=Min("details__delivery_time_in_days"),
        )

    def get_serializer_class(self):
        if self.request.method in SAFE_METHODS:
            return OfferListSerializer
        return OfferCreateSerializer

    def create(self, request, *args, **kwargs):
        """
        Use write serializer for input, but return a response serializer
        that matches frontend expectations (details without url).
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        offer = serializer.save()

        out = OfferWriteResponseSerializer(offer, context=self.get_serializer_context())
        headers = self.get_success_headers(out.data)
        return Response(out.data, status=status.HTTP_201_CREATED, headers=headers)


class OfferDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Public read (GET).
    Only the business owner can update/delete.
    """
    queryset = Offer.objects.all()
    permission_classes = [IsBusinessOwnerOrReadOnly]

    def get_serializer_class(self):
        if self.request.method in SAFE_METHODS:
            return OfferListSerializer
        return OfferCreateSerializer

    def update(self, request, *args, **kwargs):
        """
        Use write serializer for input, but return response serializer without url in details.
        """
        partial = kwargs.pop("partial", False)
        instance = self.get_object()

        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        offer = serializer.save()

        out = OfferWriteResponseSerializer(offer, context=self.get_serializer_context())
        return Response(out.data, status=status.HTTP_200_OK)


class OfferDetailDetailView(generics.RetrieveAPIView):
    queryset = OfferDetail.objects.all()
    serializer_class = OfferDetailSerializer
    permission_classes = [IsAuthenticated]


class OrderListCreateView(generics.ListCreateAPIView):
    """
    Authenticated users can list their orders.
    Customer: orders they placed
    Business: orders on their offers
    """
    permission_classes = [IsAuthenticated]
    serializer_class = OrderSerializer

    def get_throttles(self):
        if self.request.method == "POST":
            self.throttle_scope = "order_create"
            return [ScopedRateThrottle()]
        return super().get_throttles()
    
    def get_queryset(self):
        user = self.request.user
        user_profile = getattr(user, "userprofile", None)
        if user_profile is None:
            raise PermissionDenied("User profile not found.")
        if user_profile.type == "customer":
            return Order.objects.filter(customer_user=user_profile)
        if user_profile.type == "business":
            return Order.objects.filter(offer_detail__offer__user_profile=user_profile)
        return Order.objects.none()


class OrderDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Order.objects.all()
    permission_classes = [IsStaffForDeleteOrOrderPartyForReadAndBusinessOwnerForWrite]
    serializer_class = OrderSerializer


class OrderCountForBusinessView(APIView):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request, business_user_id):
        try:
            UserProfile.objects.get(id=business_user_id, type="business")
        except UserProfile.DoesNotExist:
            raise NotFound({"detail": "This id does not exist"})

        count = Order.objects.filter(
            offer_detail__offer__user_profile__id=business_user_id,
            status=Order.Status.IN_PROGRESS,
        ).count()

        return Response({"order_count": count}, status=status.HTTP_200_OK)


class CompletedOrderCountForBusinessView(APIView):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request, business_user_id):
        try:
            UserProfile.objects.get(id=business_user_id, type="business")
        except UserProfile.DoesNotExist:
            raise NotFound({"detail": "This id does not exist"})

        count = Order.objects.filter(
            offer_detail__offer__user_profile__id=business_user_id,
            status=Order.Status.COMPLETED,
        ).count()

        return Response({"completed_order_count": count}, status=status.HTTP_200_OK)



class ReviewListCreateView(generics.ListCreateAPIView):
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    ordering_fields = ["updated_at", "rating"]
    filterset_fields = ["business_user_id", "reviewer_id"]
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer

    def get_permissions(self):
        if self.request.method in SAFE_METHODS:
            return [AllowAny()]
        return [IsUserWithProfile()]


class ReviewDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer

    def get_permissions(self):
        if self.request.method in SAFE_METHODS:
            return [AllowAny()]
        return [IsReviewerSelf()]


class BaseInfoView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        average = Review.objects.aggregate(avg_rating=Avg("rating"))["avg_rating"]
        average_rating = round(average, 1) if average else 0.0

        return Response(
            {
                "review_count": Review.objects.count(),
                "average_rating": average_rating,
                "business_profile_count": UserProfile.objects.filter(type="business").count(),
                "offer_count": Offer.objects.count(),
            },
            status=status.HTTP_200_OK,
        )
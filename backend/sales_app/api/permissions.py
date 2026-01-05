from rest_framework.permissions import BasePermission, SAFE_METHODS, IsAuthenticated


class PublicReadBusinessWrite(BasePermission):
    """
    SAFE_METHODS (GET/HEAD/OPTIONS): public
    Unsafe methods: only authenticated business users
    """
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True

        user = request.user
        if not user or not user.is_authenticated:
            return False

        return hasattr(user, "userprofile") and user.userprofile.type == "business"


class IsReviewerSelf(IsAuthenticated):
    """
    Only the reviewer can modify/delete the review.
    """
    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        return hasattr(request.user, "userprofile") and request.user.userprofile == obj.reviewer


class IsUserWithProfile(BasePermission):
    """
    SAFE_METHODS: public
    Unsafe methods (POST/PATCH/PUT/DELETE): authenticated customer with profile
    """
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True

        user = request.user
        if not user or not user.is_authenticated:
            return False

        return hasattr(user, "userprofile") and user.userprofile.type == "customer"


class IsCustomerUser(IsAuthenticated):
    """
    Allow access only to authenticated customer users.
    """
    def has_permission(self, request, view):
        ok = super().has_permission(request, view)
        return ok and hasattr(request.user, "userprofile") and request.user.userprofile.type == "customer"


class IsBusinessOwnerOrReadOnly(BasePermission):
    """
    SAFE_METHODS: public
    Unsafe methods: only the business owner of the offer can modify/delete.
    """
    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True

        user = request.user
        if not user or not user.is_authenticated:
            return False

        if not hasattr(user, "userprofile"):
            return False

        return user.userprofile == obj.user_profile


from rest_framework.permissions import SAFE_METHODS, IsAuthenticated

class IsStaffForDeleteOrOrderPartyForReadAndBusinessOwnerForWrite(IsAuthenticated):
    """
    SAFE_METHODS: only parties involved can read (customer who placed it OR business who owns the offer).
    DELETE: staff/superuser only
    PATCH/PUT: business owner of the order (order belongs to their offers)
    """

    def has_object_permission(self, request, view, obj):
        user = request.user
        
        if not user or not user.is_authenticated:
            return False

        profile = getattr(user, "userprofile", None)
        is_staff = user.is_staff or user.is_superuser

        def is_order_party() -> bool:
            if is_staff:
                return True
            if not profile:
                return False
            if profile.type == "customer":
                return obj.customer_user_id == profile.id
            if profile.type == "business":
                return obj.offer_detail.offer.user_profile_id == profile.id
            return False

        if request.method in SAFE_METHODS:
            return is_order_party()

        if request.method == "DELETE":
            return is_staff

        if request.method in ("PATCH", "PUT"):
            if is_staff:
                return True
            if not profile or profile.type != "business":
                return False
            return obj.offer_detail.offer.user_profile_id == profile.id

        return False
    
class IsAuthenticatedForReadAndBusinessOwnerForWrite(BasePermission):
    """
    GET/HEAD/OPTIONS: only authenticated users (prevents 404 leak for anonymous)
    PATCH/PUT/DELETE: only business owner of the offer
    """

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True

        profile = getattr(request.user, "userprofile", None)
        if not profile:
            return False

        return profile == obj.user_profile
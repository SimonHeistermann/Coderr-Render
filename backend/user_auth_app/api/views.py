import os

from rest_framework import generics, status
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.throttling import ScopedRateThrottle

from user_auth_app.models import UserProfile
from .permissions import IsOwnerOrReadOnly
from .serializers import RegistrationSerializer, UserProfileSerializer


def format_user_profile_response(user_profile: UserProfile, request) -> dict:
    """
    Returns selected user and profile information in the response format expected by the frontend.
    """
    user = user_profile.user

    file_url = None
    if user_profile.file and user_profile.file.name:
        if request:
            file_url = request.build_absolute_uri(user_profile.file.url)
        else:
            file_url = os.path.basename(user_profile.file.name)

    return {
        "user": user_profile.id,
        "username": user.username,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "file": file_url,
        "location": user_profile.location,
        "tel": user_profile.tel,
        "description": user_profile.description,
        "working_hours": user_profile.working_hours,
        "type": user_profile.type,
        "email": user.email,
        "created_at": user_profile.created_at,
    }


class UserProfileListView(generics.ListAPIView):
    """
    Returns a list of user profiles (custom formatted). Requires authentication.
    """
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        data = [format_user_profile_response(profile, request) for profile in queryset]
        return Response(data, status=status.HTTP_200_OK)


class UserProfileBusinessListView(UserProfileListView):
    def get_queryset(self):
        return UserProfile.objects.filter(type=UserProfile.BUSINESS)


class UserProfileCustomerListView(UserProfileListView):
    def get_queryset(self):
        return UserProfile.objects.filter(type=UserProfile.CUSTOMER)


class UserProfileDetailView(generics.RetrieveUpdateAPIView):
    """
    View/update own profile. Only owner can update.
    """
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]

    def retrieve(self, request, *args, **kwargs):
        profile = self.get_object()
        return Response(format_user_profile_response(profile, request), status=status.HTTP_200_OK)

    def update(self, request, *args, **kwargs):
        profile = self.get_object()
        user = profile.user
        user.first_name = request.data.get("first_name", user.first_name)
        user.last_name = request.data.get("last_name", user.last_name)
        user.email = request.data.get("email", user.email)
        user.save()
        serializer = self.get_serializer(profile, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        return Response(format_user_profile_response(profile, request), status=status.HTTP_200_OK)


class UserProfileCreateView(generics.CreateAPIView):
    """
    Registration endpoint. Returns token + minimal user info.
    """
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "registration"
    permission_classes = [AllowAny]
    queryset = UserProfile.objects.all()
    serializer_class = RegistrationSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        profile = serializer.save()
        token, _ = Token.objects.get_or_create(user=profile.user)

        return Response(
            {
                "token": token.key,
                "username": profile.user.username,
                "email": profile.user.email,
                "user_id": profile.id,
            },
            status=status.HTTP_201_CREATED,
        )


class CustomLoginView(ObtainAuthToken):
    """
    Login endpoint. Returns token + minimal user info.
    """
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "login"
    permission_classes = [AllowAny]
    
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)

        user = serializer.validated_data["user"]
        token, _ = Token.objects.get_or_create(user=user)

        return Response(
            {
                "token": token.key,
                "username": user.username,
                "email": user.email,
                "user_id": user.userprofile.id,
            },
            status=status.HTTP_200_OK,
        )
from django.urls import path

from .views import (
    CustomLoginView,
    UserProfileBusinessListView,
    UserProfileCreateView,
    UserProfileCustomerListView,
    UserProfileDetailView,
)

urlpatterns = [
    path("registration/", UserProfileCreateView.as_view(), name="registration"),
    path("login/", CustomLoginView.as_view(), name="login"),
    path("profile/<int:pk>/", UserProfileDetailView.as_view(), name="profile-detail"),
    path("profile/<int:pk>", UserProfileDetailView.as_view(), name="profile-detail-noslash"),
    path("profiles/business/", UserProfileBusinessListView.as_view(), name="profiles-business"),
    path("profiles/customer/", UserProfileCustomerListView.as_view(), name="profiles-customer"),
]
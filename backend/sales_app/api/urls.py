from django.urls import path, include

from .views import OfferListCreateView, OfferDetailView, OfferDetailDetailView, OrderListCreateView, OrderDetailView, OrderCountForBusinessView, CompletedOrderCountForBusinessView, ReviewListCreateView, ReviewDetailView, BaseInfoView


urlpatterns = [
    path('offers/', OfferListCreateView.as_view(), name='offer-list'),
    path('offers/<int:pk>/', OfferDetailView.as_view(), name='offer-detail'),
    path('offerdetails/<int:pk>/', OfferDetailDetailView.as_view(), name='offer-detail-detail'),
    path('orders/', OrderListCreateView.as_view(), name='order-list'),
    path('orders/<int:pk>/', OrderDetailView.as_view(), name='order-detail'),
    path('order-count/<int:business_user_id>/', OrderCountForBusinessView.as_view(), name='order-count-business'),
    path('completed-order-count/<int:business_user_id>/', CompletedOrderCountForBusinessView.as_view(), name='completed-order-count-business'),
    path('reviews/', ReviewListCreateView.as_view(), name='review-list'),
    path('reviews/<int:pk>/', ReviewDetailView.as_view(), name='review-detail'),
    path('base-info/', BaseInfoView.as_view(), name='base-info')
]
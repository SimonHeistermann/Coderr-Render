from django.test import TestCase
from django.contrib.auth.models import User
from user_auth_app.models import UserProfile
from sales_app.models import Offer, OfferDetail, Order
from sales_app.admin import OfferAdmin, OfferDetailAdmin, OrderAdmin
from django.contrib.admin.sites import AdminSite

class DummyAdminSite(AdminSite):
    pass

class SalesAdminTests(TestCase):
    def setUp(self):
        self.site = DummyAdminSite()
        self.user = User.objects.create_user(username="biz", password="pw")
        self.profile = UserProfile.objects.create(user=self.user, type="business")
        self.offer = Offer.objects.create(user_profile=self.profile, title="T", description="D")
        self.detail = OfferDetail.objects.create(
            offer=self.offer, title="Basic", revisions=1, delivery_time_in_days=3,
            price="10.00", features=[], offer_type="basic"
        )
        cust_user = User.objects.create_user(username="cust", password="pw")
        cust_profile = UserProfile.objects.create(user=cust_user, type="customer")
        self.order = Order.objects.create(customer_user=cust_profile, offer_detail=self.detail)

    def test_admin_helpers(self):
        offer_admin = OfferAdmin(Offer, self.site)
        detail_admin = OfferDetailAdmin(OfferDetail, self.site)
        order_admin = OrderAdmin(Order, self.site)

        self.assertEqual(offer_admin.username(self.offer), "biz")
        self.assertEqual(detail_admin.offer_name(self.detail), "T")
        self.assertEqual(order_admin.offer_provider(self.order), self.profile)
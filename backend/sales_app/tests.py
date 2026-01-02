from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase

from user_auth_app.models import UserProfile
from sales_app.models import Offer, OfferDetail, Order, Review


class SalesApiTests(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user_business = User.objects.create_user(username="biz", password="pw123456", email="biz@test.com")
        cls.user_customer = User.objects.create_user(username="cust", password="pw123456", email="cust@test.com")
        cls.user_other = User.objects.create_user(username="other", password="pw123456", email="other@test.com")
        cls.user_no_profile = User.objects.create_user(username="noprofile", password="pw123456", email="np@test.com")
        cls.user_staff = User.objects.create_user(username="staff", password="pw123456", email="staff@test.com", is_staff=True)

        cls.profile_business = UserProfile.objects.create(user=cls.user_business, type="business")
        cls.profile_customer = UserProfile.objects.create(user=cls.user_customer, type="customer")
        cls.profile_other_customer = UserProfile.objects.create(user=cls.user_other, type="customer")
        cls.profile_staff = UserProfile.objects.create(user=cls.user_staff, type="business")  # staff can be any type

        cls.token_business = Token.objects.create(user=cls.user_business)
        cls.token_customer = Token.objects.create(user=cls.user_customer)
        cls.token_other = Token.objects.create(user=cls.user_other)
        cls.token_staff = Token.objects.create(user=cls.user_staff)
        cls.token_no_profile = Token.objects.create(user=cls.user_no_profile)

        cls.offer = Offer.objects.create(
            user_profile=cls.profile_business,
            title="Logo Design",
            description="I design a logo",
        )
        cls.detail_basic = OfferDetail.objects.create(
            offer=cls.offer,
            title="Basic",
            revisions=1,
            delivery_time_in_days=3,
            price="50.00",
            features=["a", "b"],
            offer_type="basic",
        )
        cls.detail_standard = OfferDetail.objects.create(
            offer=cls.offer,
            title="Standard",
            revisions=2,
            delivery_time_in_days=2,
            price="90.00",
            features=["a", "b", "c"],
            offer_type="standard",
        )

        cls.order = Order.objects.create(
            customer_user=cls.profile_customer,
            offer_detail=cls.detail_basic,
            status=Order.Status.IN_PROGRESS,
        )

        cls.review = Review.objects.create(
            business_user=cls.profile_business,
            reviewer=cls.profile_customer,
            rating=5,
            description="Great!",
        )

    # --------------------------
    # Helpers
    # --------------------------
    def auth(self, token: Token):
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {token.key}")

    def logout(self):
        self.client.credentials()

    def offer_payload(self, title="New Offer"):
        return {
            "title": title,
            "description": "desc",
            "details": [
                {
                    "title": "Basic",
                    "revisions": 1,
                    "delivery_time_in_days": 3,
                    "price": "10.00",
                    "features": ["x"],
                    "offer_type": "basic",
                },
                {
                    "title": "Standard",
                    "revisions": 2,
                    "delivery_time_in_days": 2,
                    "price": "20.00",
                    "features": ["x", "y"],
                    "offer_type": "standard",
                },
            ],
        }

    # --------------------------
    # Base info (public)
    # --------------------------
    def test_base_info_public(self):
        url = reverse("base-info")
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn("review_count", res.data)
        self.assertIn("average_rating", res.data)
        self.assertIn("business_profile_count", res.data)
        self.assertIn("offer_count", res.data)

    # --------------------------
    # Offers
    # --------------------------
    def test_offer_list_is_public_and_details_are_light(self):
        url = reverse("offer-list")
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        self.assertIn("results", res.data)
        self.assertGreaterEqual(len(res.data["results"]), 1)

        first = res.data["results"][0]
        self.assertIn("details", first)

        if first["details"]:
            d0 = first["details"][0]
            self.assertEqual(set(d0.keys()), {"id", "url"})

    def test_offer_create_requires_business(self):
        url = reverse("offer-list")

        self.auth(self.token_customer)
        res = self.client.post(url, self.offer_payload(), format="json")
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

        self.auth(self.token_business)
        res = self.client.post(url, self.offer_payload(title="Offer by Biz"), format="json")
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertIn("id", res.data)

        self.assertIn("details", res.data)
        self.assertGreaterEqual(len(res.data["details"]), 1)
        self.assertNotIn("url", res.data["details"][0])

    def test_offer_detail_public_read(self):
        url = reverse("offer-detail", kwargs={"pk": self.offer.id})
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn("details", res.data)
        if res.data["details"]:
            self.assertEqual(set(res.data["details"][0].keys()), {"id", "url"})

    def test_offer_update_only_owner_business(self):
        url = reverse("offer-detail", kwargs={"pk": self.offer.id})

        self.auth(self.token_other)
        res = self.client.patch(url, {"title": "Hacked"}, format="json")
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

        self.auth(self.token_business)
        res = self.client.patch(url, {"title": "Updated Title"}, format="json")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["title"], "Updated Title")

        if res.data.get("details"):
            self.assertNotIn("url", res.data["details"][0])

    def test_offer_delete_only_owner_business(self):
        offer2 = Offer.objects.create(user_profile=self.profile_business, title="To Delete", description="")
        OfferDetail.objects.create(
            offer=offer2,
            title="Basic",
            revisions=1,
            delivery_time_in_days=1,
            price="5.00",
            features=[],
            offer_type="basic",
        )
        url = reverse("offer-detail", kwargs={"pk": offer2.id})

        self.auth(self.token_other)
        res = self.client.delete(url)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

        self.auth(self.token_business)
        res = self.client.delete(url)
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)

    def test_offer_detail_detail_requires_auth(self):
        url = reverse("offer-detail-detail", kwargs={"pk": self.detail_basic.id})

        self.logout()
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

        self.auth(self.token_customer)
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn("price", res.data)

    # --------------------------
    # Orders
    # --------------------------
    def test_order_list_requires_auth_and_profile(self):
        url = reverse("order-list")

        self.logout()
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

        self.auth(self.token_no_profile)
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_order_list_customer_sees_own_orders(self):
        url = reverse("order-list")
        self.auth(self.token_customer)
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertTrue(any(o["id"] == self.order.id for o in res.data))

    def test_order_list_business_sees_orders_on_their_offers(self):
        url = reverse("order-list")
        self.auth(self.token_business)
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertTrue(any(o["id"] == self.order.id for o in res.data))

    def test_order_create_customer_ok_business_ok(self):
        url = reverse("order-list")
        payload = {"offer_detail_id": self.detail_basic.id}

        self.auth(self.token_customer)
        res = self.client.post(url, payload, format="json")
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(res.data["customer_user"], self.profile_customer.id)

        self.auth(self.token_business)
        res = self.client.post(url, payload, format="json")
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(res.data["customer_user"], self.profile_business.id)

    def test_order_detail_permissions_party_read_staff_delete_business_patch(self):
        url = reverse("order-detail", kwargs={"pk": self.order.id})

        self.auth(self.token_other)
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

        self.auth(self.token_customer)
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        self.auth(self.token_business)
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        self.auth(self.token_business)
        res = self.client.patch(url, {"status": Order.Status.COMPLETED}, format="json")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["status"], Order.Status.COMPLETED)

        self.auth(self.token_customer)
        res = self.client.patch(url, {"status": Order.Status.CANCELLED}, format="json")
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

        self.auth(self.token_staff)
        res = self.client.delete(url)
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)

    def test_order_count_endpoints(self):
        in_progress_url = reverse("order-count-business", kwargs={"business_user_id": self.profile_business.id})
        completed_url = reverse("completed-order-count-business", kwargs={"business_user_id": self.profile_business.id})

        self.auth(self.token_business)

        res = self.client.get(in_progress_url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn("order_count", res.data)

        res = self.client.get(completed_url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn("completed_order_count", res.data)

    # --------------------------
    # Reviews
    # --------------------------
    def test_reviews_public_list(self):
        url = reverse("review-list")
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_review_create_only_customer_with_profile_and_unique(self):
        url = reverse("review-list")

        self.logout()
        res = self.client.post(url, {"business_user": self.profile_business.id, "rating": 5, "description": "x"}, format="json")
        self.assertIn(res.status_code, [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN])

        self.auth(self.token_business)
        res = self.client.post(url, {"business_user": self.profile_business.id, "rating": 5, "description": "x"}, format="json")
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

        self.auth(self.token_customer)
        res = self.client.post(url, {"business_user": self.profile_business.id, "rating": 4, "description": "dup"}, format="json")
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

        self.auth(self.token_other)
        res = self.client.post(url, {"business_user": self.profile_business.id, "rating": 4, "description": "ok"}, format="json")
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(res.data["reviewer"], self.profile_other_customer.id)

    def test_review_detail_permissions_public_read_reviewer_write(self):
        url = reverse("review-detail", kwargs={"pk": self.review.id})

        self.logout()
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        self.auth(self.token_other)
        res = self.client.patch(url, {"description": "hacked"}, format="json")
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

        self.auth(self.token_customer)
        res = self.client.patch(url, {"description": "updated"}, format="json")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["description"], "updated")

        res = self.client.delete(url)
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
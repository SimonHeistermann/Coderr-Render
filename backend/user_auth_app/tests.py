from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase

from user_auth_app.models import UserProfile


class UserAuthApiTests(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user_business = User.objects.create_user(
            username="biz",
            password="pw123456",
            email="biz@test.com",
            first_name="Biz",
            last_name="Owner",
        )
        cls.profile_business = UserProfile.objects.create(user=cls.user_business, type=UserProfile.BUSINESS)

        cls.user_customer = User.objects.create_user(
            username="cust",
            password="pw123456",
            email="cust@test.com",
            first_name="Cust",
            last_name="User",
        )
        cls.profile_customer = UserProfile.objects.create(user=cls.user_customer, type=UserProfile.CUSTOMER)

        cls.user_other = User.objects.create_user(
            username="other",
            password="pw123456",
            email="other@test.com",
        )
        cls.profile_other = UserProfile.objects.create(user=cls.user_other, type=UserProfile.CUSTOMER)

        cls.token_business = Token.objects.create(user=cls.user_business)
        cls.token_customer = Token.objects.create(user=cls.user_customer)
        cls.token_other = Token.objects.create(user=cls.user_other)

    # --------------------------
    # helpers
    # --------------------------
    def auth(self, token: Token):
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {token.key}")

    def logout(self):
        self.client.credentials()

    # --------------------------
    # Registration
    # --------------------------
    def test_registration_success_creates_user_profile_and_returns_token(self):
        url = reverse("registration")
        payload = {
            "username": "newuser",
            "password": "pw123456",
            "repeated_password": "pw123456",
            "email": "newuser@test.com",
            "type": "customer",
        }

        res = self.client.post(url, payload, format="json")
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        self.assertIn("token", res.data)
        self.assertEqual(res.data["username"], "newuser")
        self.assertEqual(res.data["email"], "newuser@test.com")
        self.assertIn("user_id", res.data)

        user = User.objects.get(username="newuser")
        self.assertTrue(user.check_password("pw123456"))
        profile = UserProfile.objects.get(user=user)
        self.assertEqual(profile.type, "customer")

        self.assertTrue(Token.objects.filter(user=user).exists())

    def test_registration_rejects_duplicate_username(self):
        url = reverse("registration")
        payload = {
            "username": "biz",
            "password": "pw123456",
            "repeated_password": "pw123456",
            "email": "fresh@test.com",
            "type": "customer",
        }
        res = self.client.post(url, payload, format="json")
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("username", res.data)

    def test_registration_rejects_duplicate_email(self):
        url = reverse("registration")
        payload = {
            "username": "fresh",
            "password": "pw123456",
            "repeated_password": "pw123456",
            "email": "biz@test.com", 
            "type": "customer",
        }
        res = self.client.post(url, payload, format="json")
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("email", res.data)

    def test_registration_rejects_password_mismatch(self):
        url = reverse("registration")
        payload = {
            "username": "fresh2",
            "password": "pw123456",
            "repeated_password": "nope",
            "email": "fresh2@test.com",
            "type": "business",
        }
        res = self.client.post(url, payload, format="json")
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertTrue("non_field_errors" in res.data or "detail" in res.data)

    # --------------------------
    # Login
    # --------------------------
    def test_login_success_returns_token_and_minimal_user_info(self):
        url = reverse("login")
        payload = {"username": "cust", "password": "pw123456"}

        res = self.client.post(url, payload, format="json")
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        self.assertIn("token", res.data)
        self.assertEqual(res.data["username"], "cust")
        self.assertEqual(res.data["email"], "cust@test.com")
        self.assertEqual(res.data["user_id"], self.profile_customer.id)

    def test_login_rejects_wrong_password(self):
        url = reverse("login")
        payload = {"username": "cust", "password": "wrong"}

        res = self.client.post(url, payload, format="json")
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    # --------------------------
    # Profiles list endpoints (auth required)
    # --------------------------
    def test_profiles_business_requires_auth(self):
        url = reverse("profiles-business")

        self.logout()
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

        self.auth(self.token_customer)
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        ids = [p["user"] for p in res.data] 
        self.assertIn(self.profile_business.id, ids)
        self.assertNotIn(self.profile_customer.id, ids)

        one = res.data[0]
        for k in ("user", "username", "first_name", "last_name", "file", "location", "tel", "description", "working_hours", "type", "email", "created_at"):
            self.assertIn(k, one)

    def test_profiles_customer_requires_auth(self):
        url = reverse("profiles-customer")

        self.logout()
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

        self.auth(self.token_business)
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        ids = [p["user"] for p in res.data]
        self.assertIn(self.profile_customer.id, ids)
        self.assertIn(self.profile_other.id, ids)
        self.assertNotIn(self.profile_business.id, ids)

    # --------------------------
    # Profile detail
    # --------------------------
    def test_profile_detail_requires_auth(self):
        url = reverse("profile-detail", kwargs={"pk": self.profile_customer.id})

        self.logout()
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

        self.auth(self.token_customer)
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["user"], self.profile_customer.id)
        self.assertEqual(res.data["username"], "cust")

    def test_profile_update_only_owner_can_update(self):
        url = reverse("profile-detail", kwargs={"pk": self.profile_customer.id})

        self.auth(self.token_other)
        res = self.client.patch(url, {"location": "Berlin"}, format="json")
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

        self.auth(self.token_customer)
        payload = {
            "first_name": "New",
            "last_name": "Name",
            "email": "cust_new@test.com",
            "location": "Berlin",
            "tel": "123",
            "description": "Hi",
            "working_hours": "9-5",
            "type": "customer", 
        }
        res = self.client.patch(url, payload, format="json")
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        self.assertEqual(res.data["first_name"], "New")
        self.assertEqual(res.data["last_name"], "Name")
        self.assertEqual(res.data["email"], "cust_new@test.com")
        self.assertEqual(res.data["location"], "Berlin")
        self.assertEqual(res.data["tel"], "123")
        self.assertEqual(res.data["description"], "Hi")
        self.assertEqual(res.data["working_hours"], "9-5")

        self.profile_customer.refresh_from_db()
        self.user_customer.refresh_from_db()
        self.assertEqual(self.user_customer.first_name, "New")
        self.assertEqual(self.user_customer.last_name, "Name")
        self.assertEqual(self.user_customer.email, "cust_new@test.com")
        self.assertEqual(self.profile_customer.location, "Berlin")
        self.assertEqual(self.profile_customer.tel, "123")

    def test_profile_update_rejects_user_field_write_directly_in_serializer(self):
        """
        Your serializer has read_only_fields for user/id/created_at.
        This ensures someone can't set user via serializer fields.
        (View ignores user anyway, but we assert it doesn't change.)
        """
        url = reverse("profile-detail", kwargs={"pk": self.profile_customer.id})

        self.auth(self.token_customer)
        res = self.client.patch(url, {"user": self.profile_business.id}, format="json")
        self.assertIn(res.status_code, [status.HTTP_200_OK, status.HTTP_400_BAD_REQUEST])

        self.profile_customer.refresh_from_db()
        self.assertEqual(self.profile_customer.user_id, self.user_customer.id)
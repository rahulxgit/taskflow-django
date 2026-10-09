from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

User = get_user_model()


class AccountsAPITests(APITestCase):
    def setUp(self):
        self.register_url = reverse("auth-register")
        self.token_url = reverse("token-obtain-pair")
        self.profile_url = reverse("user-profile")

        self.user_data = {
            "email": "developer@example.com",
            "username": "developer1",
            "password": "StrongPassword123!",
            "password_confirm": "StrongPassword123!",
            "role": "DEVELOPER",
        }

    def test_user_registration_success(self):
        response = self.client.post(self.register_url, self.user_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("tokens", response.data)
        self.assertIn("access", response.data["tokens"])
        self.assertEqual(response.data["user"]["email"], self.user_data["email"])

    def test_user_registration_password_mismatch(self):
        bad_data = self.user_data.copy()
        bad_data["password_confirm"] = "DifferentPassword123!"
        response = self.client.post(self.register_url, bad_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_jwt_token_obtain(self):
        User.objects.create_user(
            email="testuser@example.com",
            username="testuser",
            password="SecurePassword123!",
        )
        response = self.client.post(
            self.token_url,
            {"email": "testuser@example.com", "password": "SecurePassword123!"},
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)

    def test_profile_access_authenticated(self):
        user = User.objects.create_user(
            email="profile@example.com",
            username="profileuser",
            password="SecurePassword123!",
        )
        self.client.force_authenticate(user=user)
        response = self.client.get(self.profile_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["email"], "profile@example.com")

    def test_profile_access_unauthenticated_fails(self):
        response = self.client.get(self.profile_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

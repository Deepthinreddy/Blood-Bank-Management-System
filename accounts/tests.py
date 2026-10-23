
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

User = get_user_model()


class AdminDashboardTests(TestCase):
    def setUp(self):
        self.admin_user = User.objects.create_user(
            username="test_admin",
            password="TestPass123!",
            role="ADMIN",
            is_active=True,
        )

        self.staff_user = User.objects.create_user(
            username="test_staff",
            password="TestPass123!",
            role="STAFF",
            is_active=True,
        )

    def test_admin_can_access_dashboard(self):
        self.client.force_login(self.admin_user)

        response = self.client.get(
            reverse("admin_dashboard")
        )

        self.assertEqual(response.status_code, 200)

    def test_staff_cannot_access_dashboard(self):
        self.client.force_login(self.staff_user)

        response = self.client.get(
            reverse("admin_dashboard")
        )

        self.assertEqual(response.status_code, 403)

    def test_logged_out_user_is_redirected_to_login(self):
        response = self.client.get(
            reverse("admin_dashboard")
        )

        self.assertRedirects(
            response,
            "/accounts/login/?next=/accounts/admin-dashboard/",
        )


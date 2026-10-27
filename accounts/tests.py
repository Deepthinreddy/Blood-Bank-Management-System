
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

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
    def test_logout_redirects_to_login(self):
        self.client.force_login(self.admin_user)

        response = self.client.post(
            reverse("logout")
        )

        self.assertRedirects(
            response,
            "/accounts/login/",
        )

        self.assertNotIn(
            "_auth_user_id",
            self.client.session,
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

from django.conf import settings
from django.test import SimpleTestCase


class SessionSettingsTests(SimpleTestCase):
 
    def test_session_cookie_age_is_30_minutes(self):
        self.assertEqual(settings.SESSION_COOKIE_AGE, 1800)

    def test_session_expires_when_browser_closes(self):
        self.assertTrue(settings.SESSION_EXPIRE_AT_BROWSER_CLOSE)

    def test_session_is_saved_on_every_request(self):
        self.assertTrue(settings.SESSION_SAVE_EVERY_REQUEST)

    def test_session_expiry_is_configured(self):
        self.assertEqual(settings.SESSION_COOKIE_AGE, 30 * 60)
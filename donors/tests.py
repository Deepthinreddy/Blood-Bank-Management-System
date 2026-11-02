from datetime import date, timedelta

from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APIClient

from .models import Donor, Donation


class DonorRegistrationTests(TestCase):
    def setUp(self):
        user_model = get_user_model()
        self.staff = user_model.objects.create_user(
            username="bloodbankstaff",
            password="test-password",
            is_staff=True,
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.staff)

        self.url = "/api/donors/"
        self.list_url = "/api/donors/list/"

        self.valid_payload = {
            "full_name": "Asha Rao",
            "date_of_birth": "2000-04-12",
            "phone_number": "+91 9876543210",
            "email": "asha@example.com",
            "address": "Bengaluru, Karnataka",
            "blood_group": "O+",
        }

    # --------------------------------------------------
    # DONOR REGISTRATION TESTS
    # --------------------------------------------------

    def test_staff_can_register_donor(self):
        response = self.client.post(
            self.url,
            self.valid_payload,
            format="json",
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(Donor.objects.count(), 1)
        self.assertEqual(Donor.objects.get().blood_group, "O+")
        self.assertIn("id", response.data)

    def test_required_fields_are_validated(self):
        payload = self.valid_payload.copy()
        payload.pop("full_name")

        response = self.client.post(
            self.url,
            payload,
            format="json",
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn("full_name", response.data)
        self.assertEqual(Donor.objects.count(), 0)

    def test_invalid_blood_group_is_rejected(self):
        payload = self.valid_payload.copy()
        payload["blood_group"] = "X+"

        response = self.client.post(
            self.url,
            payload,
            format="json",
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn("blood_group", response.data)
        self.assertEqual(Donor.objects.count(), 0)

    def test_future_date_of_birth_is_rejected(self):
        payload = self.valid_payload.copy()
        payload["date_of_birth"] = (
            date.today() + timedelta(days=1)
        ).isoformat()

        response = self.client.post(
            self.url,
            payload,
            format="json",
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn("date_of_birth", response.data)

    def test_non_staff_user_is_forbidden(self):
        user = get_user_model().objects.create_user(
            username="regularuser",
            password="test-password",
            is_staff=False,
        )
        self.client.force_authenticate(user=user)

        response = self.client.post(
            self.url,
            self.valid_payload,
            format="json",
        )

        self.assertEqual(response.status_code, 403)
        self.assertEqual(Donor.objects.count(), 0)

    def test_anonymous_user_is_rejected(self):
        self.client.force_authenticate(user=None)

        response = self.client.post(
            self.url,
            self.valid_payload,
            format="json",
        )

        self.assertIn(response.status_code, (401, 403))
        self.assertEqual(Donor.objects.count(), 0)

    # --------------------------------------------------
    # DONOR LIST AND SEARCH TESTS
    # --------------------------------------------------

    def test_staff_can_list_donors(self):
        self.client.post(
            self.url,
            self.valid_payload,
            format="json",
        )

        response = self.client.get(self.list_url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["full_name"], "Asha Rao")

    def test_staff_can_search_donors_by_name(self):
        self.client.post(
            self.url,
            self.valid_payload,
            format="json",
        )

        response = self.client.get(
            self.list_url,
            {"name": "Asha"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["full_name"], "Asha Rao")

    def test_staff_can_filter_donors_by_blood_group(self):
        self.client.post(
            self.url,
            self.valid_payload,
            format="json",
        )

        response = self.client.get(
            self.list_url,
            {"blood_group": "O+"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)

    # --------------------------------------------------
    # DONOR DETAIL TESTS
    # --------------------------------------------------

    def test_staff_can_view_donor_detail(self):
        self.client.post(
            self.url,
            self.valid_payload,
            format="json",
        )
        donor = Donor.objects.get()

        response = self.client.get(
            f"/api/donors/{donor.id}/"
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["full_name"], "Asha Rao")

    def test_staff_gets_404_for_missing_donor(self):
        response = self.client.get("/api/donors/99999/")

        self.assertEqual(response.status_code, 404)

    # --------------------------------------------------
    # DONOR UPDATE TESTS
    # --------------------------------------------------

    def test_staff_can_update_donor(self):
        self.client.post(
            self.url,
            self.valid_payload,
            format="json",
        )
        donor = Donor.objects.get()

        response = self.client.patch(
            f"/api/donors/{donor.id}/update/",
            {"address": "Updated address"},
            format="json",
        )

        self.assertEqual(response.status_code, 200)

        donor.refresh_from_db()
        self.assertEqual(donor.address, "Updated address")

    # --------------------------------------------------
    # ACCESS CONTROL TESTS
    # --------------------------------------------------

    def test_non_staff_cannot_list_donors(self):
        user = get_user_model().objects.create_user(
            username="regularuser2",
            password="test-password",
            is_staff=False,
        )
        self.client.force_authenticate(user=user)

        response = self.client.get(self.list_url)

        self.assertEqual(response.status_code, 403)

    # --------------------------------------------------
    # DONATION HISTORY TESTS
    # --------------------------------------------------

    def test_staff_can_record_donation(self):
        self.client.post(
            self.url,
            self.valid_payload,
            format="json",
        )
        donor = Donor.objects.get()

        response = self.client.post(
            f"/api/donors/{donor.id}/donations/",
            {
                "donation_date": date.today().isoformat(),
                "quantity_ml": 450,
                "notes": "First blood donation",
            },
            format="json",
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(Donation.objects.count(), 1)
        self.assertEqual(
            Donation.objects.get().quantity_ml,
            450,
        )


    def test_staff_can_retrieve_donation_history(self):
        self.client.post(
            self.url,
            self.valid_payload,
            format="json",
        )
        donor = Donor.objects.get()

        Donation.objects.create(
            donor=donor,
            donation_date=date.today(),
            quantity_ml=450,
            notes="First donation",
        )

        response = self.client.get(
            f"/api/donors/{donor.id}/donations/"
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(
            response.data[0]["quantity_ml"],
            450,
        )
        self.assertEqual(
            response.data[0]["donor_name"],
            "Asha Rao",
        )

    def test_future_donation_date_is_rejected(self):
        self.client.post(
            self.url,
            self.valid_payload,
            format="json",
        )
        donor = Donor.objects.get()

        future_date = (
            date.today() + timedelta(days=1)
        ).isoformat()

        response = self.client.post(
            f"/api/donors/{donor.id}/donations/",
            {
                "donation_date": future_date,
                "quantity_ml": 450,
                "notes": "Invalid future donation",
            },
            format="json",
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn("donation_date", response.data)
        self.assertEqual(Donation.objects.count(), 0)

    def test_non_staff_cannot_access_donation_history(self):
        self.client.post(
            self.url,
            self.valid_payload,
            format="json",
        )
        donor = Donor.objects.get()

        user = get_user_model().objects.create_user(
            username="donation_regular_user",
            password="test-password",
            is_staff=False,
        )
        self.client.force_authenticate(user=user)

        response = self.client.get(
            f"/api/donors/{donor.id}/donations/"
        )

        self.assertEqual(response.status_code, 403)

    def test_missing_donor_donation_history_returns_404(self):
        response = self.client.get(
            "/api/donors/99999/donations/"
        )

        self.assertEqual(response.status_code, 404)

    # --------------------------------------------------
    # DONOR ELIGIBILITY TESTS — F-003
    # --------------------------------------------------

    def test_staff_can_view_donor_eligibility(self):
        self.client.post(
            self.url,
            self.valid_payload,
            format="json",
        )
        donor = Donor.objects.get()

        response = self.client.get(
            f"/api/donors/{donor.id}/eligibility/"
        )

        self.assertEqual(response.status_code, 200)
        self.assertIsNone(response.data["is_eligible"])
        self.assertIsNone(response.data["eligibility_checked_at"])

    def test_staff_can_record_eligible_assessment(self):
        self.client.post(
            self.url,
            self.valid_payload,
            format="json",
        )
        donor = Donor.objects.get()

        response = self.client.patch(
            f"/api/donors/{donor.id}/eligibility/",
            {
                "is_eligible": True,
                "eligibility_notes": "Assessment recorded by staff",
            },
            format="json",
        )

        self.assertEqual(response.status_code, 200)

        donor.refresh_from_db()
        self.assertTrue(donor.is_eligible)
        self.assertEqual(
            donor.eligibility_notes,
            "Assessment recorded by staff",
        )
        self.assertIsNotNone(donor.eligibility_checked_at)

    def test_staff_can_record_ineligible_assessment(self):
        self.client.post(
            self.url,
            self.valid_payload,
            format="json",
        )
        donor = Donor.objects.get()

        response = self.client.patch(
            f"/api/donors/{donor.id}/eligibility/",
            {
                "is_eligible": False,
                "eligibility_notes": "Assessment marked ineligible",
            },
            format="json",
        )

        self.assertEqual(response.status_code, 200)

        donor.refresh_from_db()
        self.assertFalse(donor.is_eligible)
        self.assertEqual(
            donor.eligibility_notes,
            "Assessment marked ineligible",
        )
        self.assertIsNotNone(donor.eligibility_checked_at)

    def test_missing_donor_eligibility_returns_404(self):
        response = self.client.get(
            "/api/donors/99999/eligibility/"
        )

        self.assertEqual(response.status_code, 404)

    def test_non_staff_cannot_update_donor_eligibility(self):
        self.client.post(
            self.url,
            self.valid_payload,
            format="json",
        )
        donor = Donor.objects.get()

        user = get_user_model().objects.create_user(
            username="eligibility_regular_user",
            password="test-password",
            is_staff=False,
        )
        self.client.force_authenticate(user=user)

        response = self.client.patch(
            f"/api/donors/{donor.id}/eligibility/",
            {"is_eligible": True},
            format="json",
        )

        self.assertEqual(response.status_code, 403)

        donor.refresh_from_db()
        self.assertIsNone(donor.is_eligible)


class DonorFrontendTests(TestCase):
    def setUp(self):
        self.staff = get_user_model().objects.create_user(
            username="donor_frontend_staff",
            password="DonorFrontendPass123!",
            is_staff=True,
        )
        self.client.force_login(self.staff)

    def test_donor_management_page_uses_existing_donor_records(self):
        Donor.objects.create(
            full_name="Frontend Donor",
            date_of_birth=date(1994, 5, 10),
            phone_number="9876543210",
            email="frontend@example.com",
            address="Mysuru",
            blood_group="B+",
        )

        response = self.client.get("/donors/")

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Frontend Donor")
        self.assertContains(response, "Donor Management")

    def test_registration_and_profile_pages_render(self):
        registration_response = self.client.get("/donors/register/")
        donor = Donor.objects.create(
            full_name="Profile Donor",
            date_of_birth=date(1994, 5, 10),
            phone_number="9876543210",
            email="profile@example.com",
            address="Mysuru",
            blood_group="B+",
        )

        profile_response = self.client.get(f"/donors/{donor.pk}/")

        self.assertEqual(registration_response.status_code, 200)
        self.assertEqual(profile_response.status_code, 200)
        self.assertContains(profile_response, "Profile Donor")

    def test_donor_can_be_registered_from_the_frontend(self):
        response = self.client.post(
            "/donors/register/",
            {
                "full_name": "Created From UI",
                "date_of_birth": "1994-05-10",
                "phone_number": "9876543210",
                "email": "created@example.com",
                "address": "Mysuru",
                "blood_group": "B+",
            },
        )

        self.assertRedirects(response, "/donors/1/")
        self.assertTrue(
            Donor.objects.filter(full_name="Created From UI").exists()
        )
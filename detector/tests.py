import json
import os
from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from detector.models import ScanRecord
from detector.views import claim_guest_scans


class ScanRecordModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testpatient", password="Password123!")

    def test_create_scan_record_with_rich_payload(self):
        dummy_image = SimpleUploadedFile("test_scalp.jpg", b"dummy_content", content_type="image/jpeg")
        record = ScanRecord.objects.create(
            user=self.user,
            image=dummy_image,
            predicted_label="psoriasis",
            confidence=94.5,
            all_scores={"psoriasis": 94.5, "seborrheic_dermatitis": 5.5},
            is_uncertain=False,
            trichometry_metrics={"health_score": 68.0, "erythema_pct": 24.5, "flakiness_pct": 32.0},
            urgency_tier="SPECIALIST",
            urgency_badge="Dermatology Consultation Recommended",
            treatment_summary={"title": "Scalp Psoriasis Management"},
            gradcam_base64="dummy_base64_string",
        )

        self.assertEqual(record.predicted_label, "psoriasis")
        self.assertEqual(record.confidence, 94.5)
        self.assertEqual(record.trichometry_metrics["health_score"], 68.0)
        self.assertEqual(record.urgency_tier, "SPECIALIST")
        self.assertEqual(record.gradcam_base64, "dummy_base64_string")
        self.assertIn("psoriasis", str(record))


class GuestScanClaimingTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="newuser", password="Password123!")
        dummy_image = SimpleUploadedFile("guest_scan.jpg", b"guest_image_content", content_type="image/jpeg")
        self.guest_scan = ScanRecord.objects.create(
            user=None,
            image=dummy_image,
            predicted_label="dandruff",
            confidence=88.0,
            all_scores={"dandruff": 88.0},
        )

    def test_claim_guest_scans(self):
        client = Client()
        session = client.session
        session["guest_scan_ids"] = [self.guest_scan.id]
        session.save()

        # Simulate login request with session
        request = client.get(reverse("upload")).wsgi_request
        request.session = session
        request.user = self.user

        claim_guest_scans(request, self.user)

        self.guest_scan.refresh_from_db()
        self.assertEqual(self.guest_scan.user, self.user)
        self.assertEqual(request.session.get("guest_scan_ids"), [])


class ScanDetailViewTest(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username="patient1", password="Password123!")
        self.user2 = User.objects.create_user(username="patient2", password="Password123!")

        dummy_image = SimpleUploadedFile("scan1.jpg", b"image_content", content_type="image/jpeg")
        self.scan1 = ScanRecord.objects.create(
            user=self.user1,
            image=dummy_image,
            predicted_label="alopecia_areata",
            confidence=92.0,
            all_scores={"alopecia_areata": 92.0},
            trichometry_metrics={"health_score": 75.0, "erythema_pct": 5.0, "flakiness_pct": 2.0},
        )

    def test_owner_can_view_scan_detail(self):
        self.client.login(username="patient1", password="Password123!")
        response = self.client.get(reverse("scan_detail", args=[self.scan1.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Alopecia Areata")
        self.assertContains(response, "Record #")

    def test_other_user_forbidden(self):
        self.client.login(username="patient2", password="Password123!")
        response = self.client.get(reverse("scan_detail", args=[self.scan1.id]))
        self.assertEqual(response.status_code, 404)


class ScanDeletionTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="deletepatient", password="Password123!")
        self.other_user = User.objects.create_user(username="otherpatient", password="Password123!")

        dummy_image = SimpleUploadedFile("todelete.jpg", b"delete_content", content_type="image/jpeg")
        self.scan = ScanRecord.objects.create(
            user=self.user,
            image=dummy_image,
            predicted_label="folliculitis",
            confidence=85.0,
        )

    def test_owner_can_delete_scan(self):
        self.client.login(username="deletepatient", password="Password123!")
        response = self.client.post(reverse("delete_scan", args=[self.scan.id]))
        self.assertRedirects(response, reverse("dashboard"))
        self.assertFalse(ScanRecord.objects.filter(id=self.scan.id).exists())

    def test_other_user_cannot_delete_scan(self):
        self.client.login(username="otherpatient", password="Password123!")
        response = self.client.post(reverse("delete_scan", args=[self.scan.id]))
        self.assertEqual(response.status_code, 404)
        self.assertTrue(ScanRecord.objects.filter(id=self.scan.id).exists())


class DashboardViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="dashpatient", password="Password123!")
        dummy_image1 = SimpleUploadedFile("s1.jpg", b"content1", content_type="image/jpeg")
        dummy_image2 = SimpleUploadedFile("s2.jpg", b"content2", content_type="image/jpeg")

        self.scan1 = ScanRecord.objects.create(
            user=self.user,
            image=dummy_image1,
            predicted_label="psoriasis",
            confidence=95.0,
            trichometry_metrics={"health_score": 50.0, "erythema_pct": 30.0, "flakiness_pct": 25.0},
        )
        self.scan2 = ScanRecord.objects.create(
            user=self.user,
            image=dummy_image2,
            predicted_label="normal_healthy_scalp",
            confidence=99.0,
            trichometry_metrics={"health_score": 95.0, "erythema_pct": 2.0, "flakiness_pct": 1.0},
        )

    def test_dashboard_requires_login(self):
        response = self.client.get(reverse("dashboard"))
        self.assertRedirects(response, f"{reverse('login')}?next={reverse('dashboard')}")

    def test_dashboard_renders_stats_and_timeline(self):
        self.client.login(username="dashpatient", password="Password123!")
        response = self.client.get(reverse("dashboard"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["total_scans"], 2)
        self.assertTrue(response.context["has_timeline"])
        self.assertContains(response, "Longitudinal Trichometry Recovery Timeline")

    def test_dashboard_filtering_by_condition(self):
        self.client.login(username="dashpatient", password="Password123!")
        response = self.client.get(reverse("dashboard") + "?condition=psoriasis")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["scans"].count(), 1)
        self.assertEqual(response.context["scans"].first().predicted_label, "psoriasis")

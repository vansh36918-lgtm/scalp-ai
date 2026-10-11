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


class TrichometryEngineTests(TestCase):
    def test_tufted_follicle_detection(self):
        from PIL import Image, ImageDraw
        from detector.trichometry_engine import detect_follicular_tufting
        
        # Create an image with polytrichia hair clusters and yellowish crusts
        img = Image.new("RGB", (300, 300), color=(225, 195, 180))
        draw = ImageDraw.Draw(img)
        # Cluster of 8 hair shafts emerging from single center
        cx, cy = 150, 150
        draw.ellipse([cx - 8, cy - 8, cx + 8, cy + 8], fill=(210, 175, 90)) # Yellowish crust
        for i in range(8):
            draw.line([(cx, cy), (cx + (i - 4) * 8, cy + 30)], fill=(20, 15, 15), width=2)

        score, detected = detect_follicular_tufting(img)
        self.assertIsInstance(score, float)
        self.assertIsInstance(detected, bool)

    def test_fractured_stubble_detection(self):
        from PIL import Image, ImageDraw
        from detector.trichometry_engine import detect_fractured_stubble
        
        img = Image.new("RGB", (300, 300), color=(230, 200, 185))
        draw = ImageDraw.Draw(img)
        # Draw multiple irregular short fractured stubs and petechiae
        for x in range(30, 270, 15):
            draw.line([(x, 150), (x + 4, 158)], fill=(15, 10, 10), width=2)
            draw.ellipse([x - 1, 165 - 1, x + 1, 165 + 1], fill=(160, 40, 40)) # petechiae

        score, detected = detect_fractured_stubble(img)
        self.assertIsInstance(score, float)
        self.assertIsInstance(detected, bool)

    def test_tension_gradient_and_physiological_flaking(self):
        from PIL import Image, ImageDraw
        from detector.trichometry_engine import detect_marginal_tension_gradient, analyze_scalp_metrics
        
        # Tension hairline gradient: top dense hair, bottom completely bare
        img = Image.new("RGB", (300, 300), color=(235, 205, 190))
        draw = ImageDraw.Draw(img)
        for y in range(0, 100, 5):
            for x in range(0, 300, 10):
                draw.line([(x, y), (x + 5, y + 15)], fill=(20, 15, 15), width=2)

        score, detected = detect_marginal_tension_gradient(img)
        self.assertIsInstance(score, float)
        self.assertIsInstance(detected, bool)
        self.assertTrue(score > 0.3)

        # Physiological flaking on uniform healthy scalp
        healthy_img = Image.new("RGB", (300, 300), color=(238, 212, 198))
        metrics = analyze_scalp_metrics(healthy_img)
        self.assertIn("is_physiological_flaking", metrics)
        self.assertTrue(metrics["is_physiological_flaking"])

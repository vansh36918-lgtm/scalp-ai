import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "scalp_site.settings")
import django
django.setup()

from django.test import Client
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth.models import User
from detector.models import ScanRecord

client = Client()

print("--- 1. Testing GET / (Landing Page) ---")
res = client.get("/")
assert res.status_code == 200, f"Expected 200, got {res.status_code}"
assert "ScalpAI" in res.content.decode("utf-8")
assert "Clinical-Grade AI Scalp" in res.content.decode("utf-8")
print("PASS: Modern landing page loaded successfully.")

print("\n--- 2. Testing Sample Image Endpoint ---")
sample_res = client.get("/sample-image/alopecia_areata/")
assert sample_res.status_code == 200
assert sample_res["Content-Type"] == "image/jpeg"
print("PASS: Sample image endpoint returned valid JPEG.")

print("\n--- 3. Testing POST / with image ---")
import glob
test_img_path = glob.glob(os.path.join("..", "dataset", "external_test", "psoriasis", "*.*"))[0]
with open(test_img_path, "rb") as f:
    upload_file = SimpleUploadedFile("psoriasis_test.jpg", f.read(), content_type="image/jpeg")

post_res = client.post("/", {"image": upload_file})
assert post_res.status_code == 200, f"Expected 200, got {post_res.status_code}"
content = post_res.content.decode("utf-8")
assert "Psoriasis" in content
assert "Quantitative Scalp Trichometry" in content
assert "Targeted Active Ingredients" in content
assert "Download Clinical PDF Report" in content
latest_scan = ScanRecord.objects.latest("id")
assert latest_scan is not None
print(f"PASS: Inference completed. Scan #{latest_scan.id} saved: {latest_scan.predicted_label} ({latest_scan.confidence:.1f}%)")

print("\n--- 4. Testing PDF Report Generation (/report/<id>/pdf/) ---")
pdf_res = client.get(f"/report/{latest_scan.id}/pdf/")
assert pdf_res.status_code == 200
assert pdf_res["Content-Type"] == "application/pdf"
assert pdf_res.content.startswith(b"%PDF-"), "Response content does not start with %PDF- header"
print(f"PASS: PDF generation verified! Generated {len(pdf_res.content)} bytes of valid PDF.")

print("\n--- 5. Testing User Registration & Dashboard ---")
User.objects.filter(username="testpatient").delete()
reg_res = client.post("/register/", {
    "username": "testpatient",
    "email": "test@example.com",
    "password": "patientpassword123",
    "password_confirm": "patientpassword123"
}, follow=True)
assert reg_res.status_code == 200
assert "Diagnostic Screening History" in reg_res.content.decode("utf-8")
print("PASS: User registration and dashboard redirection successful.")

print("\n--- 6. Testing User Authenticated Scan & History Storage ---")
with open(test_img_path, "rb") as f:
    upload_file2 = SimpleUploadedFile("psoriasis_user.jpg", f.read(), content_type="image/jpeg")
post_res2 = client.post("/", {"image": upload_file2})
assert post_res2.status_code == 200
user_scan = ScanRecord.objects.filter(user__username="testpatient").first()
assert user_scan is not None
print(f"PASS: Authenticated scan recorded for user 'testpatient' (ID: #{user_scan.id}).")

dash_res = client.get("/dashboard/")
assert dash_res.status_code == 200
dash_html = dash_res.content.decode("utf-8")
assert f"ID: #{user_scan.id}" in dash_html
print("PASS: Scan successfully displays in user's personal dashboard table.")

print("\n--- 7. Testing Admin Panel Access ---")
admin_res = client.get("/admin/login/")
assert admin_res.status_code == 200
print("PASS: Admin panel is accessible at /admin/.")

print("\n=======================================================")
print("ALL CLINICAL PORTAL, PDF, AND AUTH TESTS PASSED 100%!")
print("=======================================================")

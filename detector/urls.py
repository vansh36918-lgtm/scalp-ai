from django.urls import path
from . import views

urlpatterns = [
    path("", views.upload_view, name="upload"),
    path("ping/", views.ping_view, name="ping"),
    path("report/<int:scan_id>/pdf/", views.download_pdf_view, name="download_pdf"),
    path("dashboard/", views.dashboard_view, name="dashboard"),
    path("scan/<int:scan_id>/delete/", views.delete_scan_view, name="delete_scan"),
    path("sample-image/<str:class_name>/", views.sample_image_view, name="sample_image"),
    path("download-presentation/", views.download_presentation_view, name="download_presentation"),
    path("register/", views.register_view, name="register"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
]

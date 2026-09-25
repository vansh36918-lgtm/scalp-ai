from django.urls import path
from . import views

urlpatterns = [
    path("", views.upload_view, name="upload"),
    path("report/<int:scan_id>/pdf/", views.download_pdf_view, name="download_pdf"),
    path("dashboard/", views.dashboard_view, name="dashboard"),
    path("sample-image/<str:class_name>/", views.sample_image_view, name="sample_image"),
    path("register/", views.register_view, name="register"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
]

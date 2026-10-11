from django.db import models
from django.contrib.auth.models import User

class ScanRecord(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="scans")
    image = models.ImageField(upload_to="scans/%Y/%m/")
    predicted_label = models.CharField(max_length=100)
    confidence = models.FloatField()
    all_scores = models.JSONField(default=dict)
    is_uncertain = models.BooleanField(default=False)
    trichometry_metrics = models.JSONField(default=dict, blank=True)
    urgency_tier = models.CharField(max_length=50, blank=True, default="")
    urgency_badge = models.CharField(max_length=100, blank=True, default="")
    treatment_summary = models.JSONField(default=dict, blank=True)
    gradcam_base64 = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        user_str = self.user.username if self.user else "Guest"
        return f"{self.predicted_label} ({self.confidence:.1f}%) - {user_str} [{self.created_at.strftime('%Y-%m-%d %H:%M')}]"

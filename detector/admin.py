from django.contrib import admin
from django.utils.html import format_html
from .models import ScanRecord

@admin.register(ScanRecord)
class ScanRecordAdmin(admin.ModelAdmin):
    list_display = ("id", "thumbnail", "predicted_label", "confidence_badge", "user_display", "is_uncertain", "created_at")
    list_filter = ("predicted_label", "is_uncertain", "created_at")
    search_fields = ("predicted_label", "user__username", "notes")
    readonly_fields = ("created_at", "thumbnail_large")
    date_hierarchy = "created_at"

    def user_display(self, obj):
        return obj.user.username if obj.user else "Guest"
    user_display.short_description = "User"

    def thumbnail(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="width: 45px; height: 45px; object-fit: cover; border-radius: 4px;" />', obj.image.url)
        return "-"
    thumbnail.short_description = "Image"

    def thumbnail_large(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="max-width: 300px; max-height: 300px; border-radius: 8px;" />', obj.image.url)
        return "-"
    thumbnail_large.short_description = "Uploaded Scalp Image"

    def confidence_badge(self, obj):
        color = "#10b981" if obj.confidence >= 75 else ("#f59e0b" if obj.confidence >= 50 else "#ef4444")
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; border-radius: 12px; font-weight: bold; font-size: 11px;">{:.1f}%</span>',
            color,
            obj.confidence,
        )
    confidence_badge.short_description = "Confidence"

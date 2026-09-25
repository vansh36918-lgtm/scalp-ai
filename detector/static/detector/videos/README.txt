Place your custom background video file here:
Filename: hero_bg.mp4
Path: django_app/detector/static/detector/videos/hero_bg.mp4

The landing page HTML automatically checks for this local file first:
{% static 'detector/videos/hero_bg.mp4' %}
If not found, it gracefully falls back to the online high-resolution ambient medical AI animation video.

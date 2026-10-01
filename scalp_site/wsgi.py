import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "scalp_site.settings")
application = get_wsgi_application()

# Preload TensorFlow ML model into memory at startup to eliminate first-request latency & Gunicorn timeouts
try:
    from detector.ml_model import _load
    _load()
    print("ScalpAI Model Preloaded Successfully at Startup!")
except Exception as e:
    print("Model preload notice:", e)

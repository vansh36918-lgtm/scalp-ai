FROM python:3.10-slim

ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Install minimal OS dependencies for OpenCV / PIL / ReportLab
RUN apt-get update && apt-get install -y \
    build-essential \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Expose port
EXPOSE 8000

CMD ["sh", "-c", "gunicorn --bind 0.0.0.0:${PORT:-8000} scalp_site.wsgi:application"]

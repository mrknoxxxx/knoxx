```dockerfile
FROM python:3.11-slim

# Python logs ko buffer na kare
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# FFmpeg install
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Requirements install
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Project files copy
COPY . .

# Port
EXPOSE 10000

# Start Gunicorn
CMD ["gunicorn", "app:app", \
     "--bind", "0.0.0.0:10000", \
     "--workers", "2", \
     "--threads", "2", \
     "--timeout", "120"]
```

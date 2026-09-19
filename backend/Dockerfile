FROM python:3.11-slim

WORKDIR /app

# Ensure Python outputs are sent straight to terminal without buffering
ENV PYTHONUNBUFFERED=1

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    espeak-ng \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend source code
COPY . .

# Ensure Vosk offline speech recognition model is available at container build time
RUN python -c "import os, urllib.request, zipfile; m='models/vosk-model-small-en-us-0.15'; os.makedirs('models', exist_ok=True); (not os.path.exists(m)) and (urllib.request.urlretrieve('https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip', 'models/m.zip'), zipfile.ZipFile('models/m.zip').extractall('models'), os.remove('models/m.zip'))"

# Run Uvicorn dynamically bound to Cloud Run / container PORT environment variable (default 8080)
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8080}"]


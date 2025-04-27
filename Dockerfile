# ================================================
# Stage 1: Build Stage
# ================================================

FROM python:3.11-slim-bookworm AS builder

WORKDIR /app

# Install system dependencies needed to build packages like spacy, sentencepiece, etc.
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    build-essential \
    python3-dev \
    libc6-dev \
    libffi-dev \
    libssl-dev \
    wget \
    && rm -rf /var/lib/apt/lists/*

# Copy only requirements.txt first (better build caching)
COPY backend/requirements.txt .

# Upgrade pip and install Python dependencies into /install
RUN pip install --upgrade pip
RUN pip install --prefix=/install --no-cache-dir -r requirements.txt

# ================================================
# Stage 2: Production Stage
# ================================================

FROM python:3.11-slim-bookworm

WORKDIR /app

# Copy installed Python packages from builder
COPY --from=builder /install /usr/local

# Copy backend application code
COPY backend/main.py ./main.py
COPY backend/model ./model

# Copy frontend built static files (make sure you run npm run build before!)
COPY frontend/dist ./static

# Expose port
EXPOSE 8000

# Start FastAPI server
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
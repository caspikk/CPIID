# ================================================
# Stage 1: Build Stage
# ================================================

FROM python:3.13-slim-bookworm AS builder

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Only copy requirements.txt first
COPY backend/requirements.txt .

# Install Python dependencies
RUN pip install --upgrade pip
RUN pip install --prefix=/install --no-cache-dir -r requirements.txt

# ================================================
# Stage 2: Final Stage
# ================================================

FROM python:3.13-slim-bookworm

WORKDIR /app

# Copy installed dependencies
COPY --from=builder /install /usr/local

# Copy only backend Python code
COPY backend/main.py ./main.py
COPY backend/model ./model

# Copy only built frontend
COPY frontend/dist ./static

# Expose the port
EXPOSE 8000

# Start the server
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
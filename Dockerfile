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

# Install Python dependencies into a temporary directory
COPY backend/requirements.txt .
RUN pip install --upgrade pip
RUN pip install --prefix=/install --no-cache-dir -r requirements.txt

# ================================================
# Stage 2: Production Stage
# ================================================

FROM python:3.13-slim-bookworm

WORKDIR /app

# Copy installed dependencies from builder stage
COPY --from=builder /install /usr/local

# Copy backend application code
COPY backend/ .

# Copy frontend built files (already built via npm run build)
COPY frontend/dist ./static

# Expose port
EXPOSE 8000

# Start the app
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
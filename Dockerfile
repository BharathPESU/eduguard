# ════════════════════════════════════════════════════════════
# EduGuard AI — Backend Dockerfile
# Python 3.12 · FastAPI · Uvicorn
# ════════════════════════════════════════════════════════════

FROM python:3.12-slim AS base

# System deps needed by PyMuPDF + Pillow
RUN apt-get update && apt-get install -y --no-install-recommends \
    libglib2.0-0 \
    libgl1 \
    libgomp1 \
    gcc \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python deps first (layer cache friendly)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application source
COPY app/       ./app/
COPY rules/     ./rules/

# Create runtime directories (PYQ sessions backup folder)
RUN mkdir -p data/pyq_sessions storage/documents

# Cloud Run injects PORT env var; default to 8000 for local
ENV PORT=8000
ENV PYQ_SESSIONS_DIR=/app/data/pyq_sessions

# Non-root user for security
RUN adduser --disabled-password --gecos "" appuser \
    && chown -R appuser:appuser /app
USER appuser

EXPOSE 8080

CMD uvicorn app.main:app --host 0.0.0.0 --port ${PORT}

# AlphaForge Backend Dockerfile
# Build a lightweight image to run FastAPI (uvicorn) backend

FROM python:3.11-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# System dependencies (for scientific Python, sklearn, and TA-Lib)
RUN apt-get update \
 && apt-get install -y --no-install-recommends \
    build-essential \
    libgomp1 \
    wget \
    tar \
 && rm -rf /var/lib/apt/lists/*

# Install TA-Lib C Library
WORKDIR /tmp
RUN wget http://prdownloads.sourceforge.net/ta-lib/ta-lib-0.4.0-src.tar.gz \
 && tar -xvzf ta-lib-0.4.0-src.tar.gz \
 && cd ta-lib \
 && ./configure --prefix=/usr \
 && make \
 && make install \
 && cd .. \
 && rm -rf ta-lib ta-lib-0.4.0-src.tar.gz

# Install Python dependencies first (leverage Docker layer caching)
WORKDIR /tmp
COPY requirements_optimized.txt /tmp/requirements.txt
RUN pip install --upgrade pip \
 && pip install --no-cache-dir -r /tmp/requirements.txt

# App
WORKDIR /app/backend
COPY . /app/backend

# Expose API port
EXPOSE 5000

# Default database path inside container (SQLite)
ENV DATABASE_URL=sqlite:///./trading_signals.db

# Start the API server
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "5000"]

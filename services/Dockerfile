# Use Python 3.11 slim image as base
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DEBIAN_FRONTEND=noninteractive

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first to leverage Docker cache
COPY reqs.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r reqs.txt

# Copy the application code
COPY ./ ./

# Create necessary directories for data persistence
RUN mkdir -p /app/data

# Set environment variables for data directories
ENV INPUT_DIR=/app/data \
    OUTPUT_DIR=/app/data

# Set default command
CMD ["python", "analyze_wallets.py", "-i", "/app/data/wallets.json", "-o", "/app/data/wallet_analysis.json"]
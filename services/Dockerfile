# Use Python 3.12 slim image as base
FROM python:3.12-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DEBIAN_FRONTEND=noninteractive \
    INPUT_DIR=/app/data \
    OUTPUT_DIR=/app/data

# Set working directory
WORKDIR /app/

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy only the requirements first to leverage Docker cache
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy service files
COPY . .

# Create data directory and set it as a volume
RUN mkdir -p /app/data
VOLUME /app/data

# Set default command to analyze wallets with standard paths
ENTRYPOINT ["python", "analyze_wallets.py"]
CMD ["-i", "/app/data/ton_wallets.json", "-o", "/app/data/wallet_analysis.json"]
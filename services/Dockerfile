# Use Python 3.12 slim image as base
FROM python:3.12-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DEBIAN_FRONTEND=noninteractive

# Set working directory
WORKDIR /app/services

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy only the requirements first to leverage Docker cache
COPY services/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy service files
COPY services/ .

# Create necessary directories for data persistence
RUN mkdir -p /app/data

# Set environment variables for data directories
ENV INPUT_DIR=/app/data \
    OUTPUT_DIR=/app/data

# Set the default command to help text
CMD ["python", "-c", "print('Available scripts:\\n- analyze_wallets.py\\n- find_wallets.py\\n- transactions.py\\nRun with: docker run <image> python <script_name> [args]')"]
FROM python:3.12-slim AS builder

#ENV PYTHONUNBUFFERED=1
WORKDIR /code

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    zlib1g-dev \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY ./requirements.txt .
RUN python -m venv /opt/venv && \
    /opt/venv/bin/pip install --no-cache-dir -r requirements.txt \

#FROM python:3.12-slim

#ENV PYTHONUNBUFFERED=1 \
#    PATH="/opt/venv/bin:$PATH"

#WORKDIR /code

RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev \
    libjpeg62 \
    zlib1g \
    libmagic1 \
    netcat-traditional \
    dos2unix \
 && rm -rf /var/lib/apt/lists/* \

COPY --from=builder /opt/venv /opt/venv
COPY . .

RUN dos2unix /app/entrypoint.sh && chmod +x /app/entrypoint.sh

# Expose port for Gunicorn
EXPOSE 8000

# Default command
ENTRYPOINT ["/app/entrypoint.sh"]

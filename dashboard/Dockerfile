FROM python:3.12-slim

WORKDIR /app


# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    zlib1g-dev \
    build-essential \
    netcat-traditional \
    && rm -rf /var/lib/apt/lists/*


COPY . .
RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 8501

RUN chmod +x /app/entrypoint.sh
ENTRYPOINT ["/app/entrypoint.sh"]

FROM python:3.12-slim

#ENV PYTHONUNBUFFERED=1
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    zlib1g-dev \
    build-essential \
    netcat-traditional \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY ./requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt gunicorn

# Expose port for Gunicorn
EXPOSE 8000
CMD ["gunicorn", "--bind", "127.0.0.1:8000", "miniDice.wsgi:application"]

COPY . .

COPY entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh
# Default command
ENTRYPOINT ["/app/entrypoint.sh"]

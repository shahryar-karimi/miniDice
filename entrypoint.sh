#!/bin/bash
set -e

function exit_with_error {
    echo "Error: $1"
    exit 1
}
# There are some times database is not ready yet!
# We'll check if database is ready and we can connect to it
# then the rest of the code run as well.
#env > .env
if [ -z "$POSTGRES_DB" ] || [ -z "$POSTGRES_HOST" ] || [ -z "$POSTGRES_PORT" ]; then
    echo "Database environment variables are empty. Skipping database connection check."
else
    echo "Waiting for database..."
    echo "DB_NAME: $POSTGRES_DB"
    echo "DB_HOST: $POSTGRES_HOST"
    echo "DB_PORT: $POSTGRES_PORT"
    while ! nc -z "$POSTGRES_HOST" "$POSTGRES_PORT"; do
        sleep 1
    done
    echo "Connected to database."
fi

if [ "${MIGRATE}" == 'True' ]; then
    echo "Running migrate..."
    python manage.py migrate --no-input || exit_with_error "Failed to migrate database"
fi
echo "Initializing default superuser..."
python manage.py initadmin --email=$DJANGO_SUPERUSER_EMAIL --full_name="$DJANGO_SUPERUSER_FULL_NAME" --password=$DJANGO_SUPERUSER_PASSWORD
status=$?
if [ $status -ne 0 ]; then
    echo "Failed to initialize default admin: $status"
    exit $status
fi
if [ "${COLLECT_STATIC}" == 'True' ]; then
    echo "Collecting static files..."
    python manage.py collectstatic --no-input || exit_with_error "Failed to collect static files"
fi
echo "Starting Project..."

if [ "$DJANGO_ENV" == "prod" ]; then
    echo "Starting Gunicorn in production mode..."
    gunicorn miniDice.wsgi:application --bind 0.0.0.0:8000 --workers 3
else
    echo "Starting Django development server..."
    python manage.py runserver 0.0.0.0:8000
#    python ./telegram_bot_run.py
fi

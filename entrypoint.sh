#!/bin/bash

set -e

# There are some times database is not ready yet!
# We'll check if database is ready and we can connect to it
# then the rest of the code run as well.
#env > .env

#echo "Waiting for database..."
#echo DB_NAME: ${DB_NAME}
#echo DB_HOST: ${DB_HOST}
#echo DB_PORT: ${DB_PORT}
#while ! nc -z ${DB_HOST} ${DB_PORT}; do sleep 1; done
#echo "Connected to database."

if [ ${MIGRATE} == 'True' ]; then
    python manage.py migrate --no-input
    status=$?
    if [ $status -ne 0 ]; then
        echo "Failed to migrate database: $status"
        exit $status
    fi
fi

if [ ${COLLECT_STATIC} == 'True' ]; then
    python manage.py collectstatic --no-input
    status=$?
    if [ $status -ne 0 ]; then
        echo "Failed to collect staticfiles: $status"
        exit $status
    fi
fi

# shellcheck disable=SC3006
#if [ -z ${DJANGO_DEBUG+x} ] || (( "$DJANGO_DEBUG" == "true" ))
#then
#    nodemon --exec ipython ./telegram_bot_run.py
#else
#fi
python ./telegram_bot_run.py

gunicorn
#!/bin/sh

set -e

sleep 7


python manage.py migrate --noinput

# shellcheck disable=SC3006
if [ -z ${DJANGO_DEBUG+x} ] || (( "$DJANGO_DEBUG" == "true" ))
then
    nodemon --exec ipython ./telegram_bot_run.py
else
    python ./telegram_bot_run.py
fi
#!/bin/bash -x
poetry install --no-dev --no-interaction
python manage.py migrate --noinput || exit 1
exec "$@"

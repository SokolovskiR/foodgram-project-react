#!/bin/bash

echo "collect static files"
python manage.py collectstatic --noinput

echo "makemigrations"
python manage.py makemigrations --noinput

echo "migrate"
python manage.py migrate --noinput

exec "$@"
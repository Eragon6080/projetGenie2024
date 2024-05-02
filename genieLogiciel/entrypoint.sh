#!/bin/sh

# Attendre que la base de données soit prête


python manage.py migrate
python manage.py runserver 0.0.0.0:8000
exec "$@"
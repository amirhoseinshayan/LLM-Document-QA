#!/bin/sh

# Stop the script if any command fails.
set -e

# Apply database migrations before starting the server.
python manage.py migrate --noinput

# Collect static files for Docker environment.
python manage.py collectstatic --noinput

# Start the Django development server.
python manage.py runserver 0.0.0.0:8000
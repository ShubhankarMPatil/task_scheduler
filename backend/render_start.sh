#!/usr/bin/env bash
set -euo pipefail

# Render sets PORT; default for local usage.
export PORT="${PORT:-8000}"

python manage.py migrate --noinput
python manage.py collectstatic --noinput

# Use gunicorn for production
exec gunicorn core.wsgi:application --bind 0.0.0.0:"$PORT" --workers 2 --threads 4 --timeout 120

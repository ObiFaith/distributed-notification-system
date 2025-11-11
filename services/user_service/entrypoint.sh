#!/usr/bin/env bash
set -e

export FLASK_APP=${FLASK_APP:-wsgi.py}

echo "🔧 Running database migrations (user_service)..."
until flask db upgrade; do
  echo "DB not ready yet, retrying in 3s..."
  sleep 3
done

echo "🚀 Starting user_service..."
exec gunicorn -w 2 -b 0.0.0.0:8000 wsgi:app

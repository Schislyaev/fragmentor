#!/bin/sh

echo "Waiting for Postgres..."
while ! nc -z $DB_HOST $DB_PORT; do sleep 0.1
done
echo "Postgres started"

echo "Waiting for Redis..."
while ! nc -z $REDIS_HOST $REDIS_PORT; do
  sleep 0.1
done
echo "Redis started"

export PYTHONPATH="${PYTHONPATH}:/opt/app"
gunicorn server.main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8080 --timeout 120
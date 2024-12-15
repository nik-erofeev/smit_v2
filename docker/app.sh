#!/bin/bash

#  вместо статического ожидания + postgresql-client в dockerfile
#sleep 5
echo "Waiting for PostgreSQL to start..."
until pg_isready -h postgres -U newuser; do
  sleep 1
done

echo "Starting migrations..."
alembic upgrade head


echo Check migration status
MIGRATION_STATUS=$?
if [ $MIGRATION_STATUS -ne 0 ]; then
  echo "Migrations failed with status $MIGRATION_STATUS"
  exit 1
fi


echo "Waiting for Kafka to start..."
#  вместо статического ожидания + netcat-openbsd в dockerfile
# sleep 10
while ! nc -z kafka 9092; do
  sleep 1
done


echo "Starting FastAPI server..."
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
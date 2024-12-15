#!/bin/bash


echo "Waiting for 1 seconds to allow PostgreSQL to start..."
sleep 1

echo "Starting migrations..."
alembic upgrade head


echo Check migration status
MIGRATION_STATUS=$?
if [ $MIGRATION_STATUS -ne 0 ]; then
  echo "Migrations failed with status $MIGRATION_STATUS"
  exit 1
fi


echo "Waiting for Kafka to start..."
# sleep 10  # или так
while ! nc -z kafka 9092; do
  sleep 1
done


echo "Starting FastAPI server..."
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
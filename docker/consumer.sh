#!/bin/bash

echo "Waiting for Kafka to start..."
while ! nc -z kafka 9092; do
  sleep 1
done

echo "Kafka is up and running. Starting RabbitMQ consumer..."

python app/main_rabbit_consumer.py
# python -m app.main_rabbit_consumer

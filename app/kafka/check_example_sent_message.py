import asyncio

from app.kafka.producer import KafkaProducer


async def test_kafka_producer():
    producer = KafkaProducer(
        bootstrap_servers="localhost:29092",
        default_topic="my_example_topik",
    )
    await producer.start()

    test_message = {"test": "message"}

    # await producer.send_message(test_message, "new_topic") # в новый топик
    await producer.send_message(test_message)

    await producer.stop()


if __name__ == "__main__":
    asyncio.run(test_kafka_producer())

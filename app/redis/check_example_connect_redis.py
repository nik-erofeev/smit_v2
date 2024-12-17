import asyncio
import json

import redis.asyncio as aioredis


async def main():
    redis = aioredis.from_url("redis://localhost")

    try:
        keys = await redis.keys("*")
        if keys:
            decoded_keys = [key.decode("utf-8") for key in keys]
            print("Key's:", decoded_keys)
        else:
            print("Данные отсутствуют")

    except Exception as e:
        print("Ошибка при подключении к Redis:", e)
        return

    key = "EXAMPLE_KEY"
    value = "EXAMPLE_VALUE"

    await redis.set(key, value)
    value = await redis.get(key)

    decoded_value = value.decode("utf-8") if value else None

    json_output = json.dumps({key: decoded_value})

    print(json_output)


if __name__ == "__main__":
    asyncio.run(main())

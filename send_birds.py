from common import log, send_message
from random_bird import get_random_bird
import aiohttp
import asyncio


async def _send_bird_message(app, item, session):
    try:
        num = item["phone_number"]["S"]
        bird = await get_random_bird(app, session)
        name = bird["name"]
        url = bird["image"]
        r = await send_message(app, num, name, url)
        print(r)
    except Exception as e:
        log(f"failed to send bird message to {item}: {e}")


async def _bird_job(app):
    try:
        dynamodb = app.config["dynamodb_client"]
        r = dynamodb.scan(TableName="bird_bot_subscribers")
        async with aiohttp.ClientSession() as session:
            items = r["Items"]
            for i in items:
                await _send_bird_message(app, i, session)
            
            await session.close()
    except Exception as e:
        print(e)


def send_birds(app):
    log("starting bird job")
    asyncio.run(_bird_job(app))
    
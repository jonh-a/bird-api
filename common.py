import aiohttp


async def send_message(app, to, message, url=None):
    """
    send a text through telnyx's api

    send_message(app, "+15555555555", "test")
    """
    try:
        async with aiohttp.ClientSession() as session:
            data = {
                "from": f"+{app.config['telnyx_number']}",
                "to": to,
                "text": message
            }

            if url is not None:
                data["media_urls"] = [url]

            async with session.post(
                "https://api.telnyx.com/v2/messages",
                json=data,
                headers={
                    "Authorization": f"Bearer {app.config['telnyx_api_key']}"
                }
            ) as response:
                log(f"message response: {await response.json()}")
                if response.status == 200:
                    await session.close()
                    return True
                else:
                    log(f"error sending message: {response.data}")
                    await session.close()
                    return False
                
    except Exception as e:
        return False


def log(message):
    """
    the most advanced python logging framework ever developed
    """
    print(f" + {message}")
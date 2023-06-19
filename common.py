import aiohttp

async def send_message(app, to, message):
    try:
        async with aiohttp.ClientSession() as session:
            data = {
                "from": f"+{app.config['telnyx_number']}",
                "to": to,
                "text": message
            }

            async with session.post(
                "https://api.telnyx.com/v2/messages",
                json=data,
                headers={
                    "Authorization": f"Bearer {app.config['telnyx_api_key']}"
                }
            ) as response:
                print(f" + message response: {await response.json()}")
                if response.status == 200:
                    return True
                else:
                    print(response.data)
                    return False
    except Exception as e:
        return False
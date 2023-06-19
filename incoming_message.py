from common import send_message

def _add_number_to_db(dynamodb, number):
    try:
        r = dynamodb.put_item(
                TableName="bird_bot_subscribers",
                Item={'phone_number': {'S': number}},
            )
        return True
    except Exception as e:
        print(' + failed to add item to database', e)
        return False


def _remove_number_from_db(dynamodb, number):
    try:
        r = dynamodb.delete_item(
                TableName="bird_bot_subscribers",
                Key={'phone_number': {'S': number}},
            )
        return True
    except Exception as e:
        print(' + failed to remove item from database', e)
        return False


async def _new_subscriber(app, dynamodb, number):
    try:
        r = _add_number_to_db(dynamodb, number)
        if r is False:
            return False
            
        r = await send_message(app, number, "subscribed to bird bot - you'll get a bird every day. reply stop to unsubscribe.")
        if r is False:
            return False
        
        return True
    except Exception as e:
        print(e)
        return False


async def _unsubscribe(app, dynamodb, number):
    try:
        r = _remove_number_from_db(dynamodb, number)
        if r is False:
            return False
            
        r = await send_message(app, number, 'successfully unsubscribed :(')
        if r is False:
            return False
        
        return True
    except Exception as e:
        print(e)
        return False

async def incoming_message(app, body):
    try:
        dynamodb = app.config["dynamodb_client"]
        event_type = body["data"]["event_type"]
        if event_type != "message.received":
            return False

        _from = body["data"]["payload"]["from"]["phone_number"]
        text = body["data"]["payload"]["text"]

        if text.lower().strip() == "bird":
            r = await _new_subscriber(app, dynamodb, _from)
            return r
        
        if text.lower().strip() == "stop":
            r = await _unsubscribe(app, dynamodb, _from)
            return r
        
        return False

    except Exception as e:
        print(e)
        return False
    
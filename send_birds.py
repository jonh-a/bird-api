async def send_birds(app):
    print(' + starting bird job')
    try:
        dynamodb = app.config["dynamodb_client"]
        r = dynamodb.scan(TableName="bird_bot_subscribers")

        items = r["Items"]

        print(items)
    except Exception as e:
        print(e)
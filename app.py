import datetime
import aiohttp
import asyncio
import os

from flask import Flask, jsonify, request
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from dotenv import load_dotenv
import boto3

from random_bird import get_random_bird
from send_birds import send_birds
from incoming_message import incoming_message

load_dotenv()

app = Flask(__name__)
app.config["aws_access_key"] = os.getenv("AWS_ACCESS_KEY", "")
app.config["aws_secret_access_key"] = os.getenv("AWS_SECRET_ACCESS_KEY", "")
app.config["telnyx_api_key"] = os.getenv("TELNYX_API_KEY", "")
app.config["telnyx_number"] = os.getenv("TELNYX_NUMBER", "")
app.config["birds"] = []
app.config["last_refreshed"] = datetime.datetime.now()

dynamodb = boto3.client(
    'dynamodb',
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY", ""),
    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY", ""),
    region_name="us-east-1"
)

app.config["dynamodb_client"] = dynamodb
asyncio.run(send_birds(app))

limiter = Limiter(
    app,
    key_func=get_remote_address,
)

@app.route("/health")
def health():
    return jsonify({"status": "OK"})


@app.route("/random")
@limiter.limit("100 per hour")
async def random():
    try:
        async with aiohttp.ClientSession() as session:
            b = await get_random_bird(app, session)
            return jsonify(b)
    except Exception as e:
        print(e)
        return jsonify({"error": "an unexpected error occurred."})

@app.route("/webhook", methods=["POST"])
async def webhook():
    body = request.get_json()
    r = await incoming_message(app, body)
    return jsonify({"status": "ok"})


@app.errorhandler(429)
def rate_limit_handler(e):
    return jsonify({"error": "rate limit exceeded."})


if __name__ == "__main__":
    app.run(debug=True)
    
    

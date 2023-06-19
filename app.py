import datetime
import aiohttp
import asyncio
import os

from flask import Flask, jsonify, request
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from apscheduler.schedulers.background import BackgroundScheduler
from dotenv import load_dotenv
from pytz import timezone
import boto3

from random_bird import get_random_bird
from send_birds import send_birds
from incoming_message import incoming_message

VERSION='1.0.1'

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

limiter = Limiter(
    app,
    key_func=get_remote_address,
)

@app.route("/health")
def health():
    return jsonify({"status": "OK"})


@app.route("/version")
def version():
    return jsonify({"version": VERSION})


@app.route("/random")
@limiter.limit("100 per hour")
async def random():
    try:
        async with aiohttp.ClientSession() as session:
            b = await get_random_bird(app, session)
            await session.close()
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
    scheduler = BackgroundScheduler()
    scheduler.add_job(send_birds, "cron", hour=19, minute=0, timezone=timezone('UTC'), args=[app])
    scheduler.start()
    app.run()
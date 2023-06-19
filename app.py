from flask import Flask, jsonify
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from random_bird import get_random_bird
import datetime
import aiohttp

app = Flask(__name__)
app.config["birds"] = []
app.config["last_refreshed"] = datetime.datetime.now()

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
    async with aiohttp.ClientSession() as session:
        b = await get_random_bird(app, session)
        return jsonify(b)


@app.errorhandler(429)
def rate_limit_handler(e):
    return jsonify({"error": "Rate limit exceeded."})


if __name__ == "__main__":
    app.run(debug=True)

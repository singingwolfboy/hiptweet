import json
from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from flask_dance.contrib.twitter import twitter
from hiptweet import db

webhook = Blueprint('webhook', __name__)


@webhook.route("/room_message", methods=["POST"])
@login_required
def room_message():
    try:
        fields = json.loads(request.data.decode('utf-8'))
    except ValueError:
        return "invalid JSON", 400
    message = fields["item"]["message"]["message"]
    if message.startswith("/tweet "):
        message = message[7:]
    resp = twitter.post("statuses/update", data={
        "status": message,
    })
    if not resp.ok:
        return jsonify({
            "message": "Failed to tweet :(",
            "message_format": "text",
        })
    result = resp.json()
    tweet_id = result["id"]
    screen_name = result["user"]["screen_name"]
    tweet_url = "https://twitter.com/{screen_name}/status/{tweet_id}".format(
        screen_name=screen_name,
        tweet_id=tweet_id,
    )
    return jsonify({
        "message": tweet_url,
        "message_format": "text",
    })

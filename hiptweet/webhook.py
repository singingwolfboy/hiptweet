import json
from flask import Blueprint, request, jsonify, current_app, render_template
from flask_login import login_required
from flask_dance.contrib.twitter import twitter

webhook = Blueprint('webhook', __name__)


@webhook.route("/room_message", methods=["POST"])
@login_required
def room_message():
    try:
        fields = json.loads(request.data.decode('utf-8'))
    except ValueError:
        return "invalid JSON", 400
    message = fields["item"]["message"]["message"]
    if not message.startswith("/tweet"):
        current_app.logger.warning(
            "Received a non-tweet message: %s (ignored)",
            message,
        )
        return "ignored"

    if message.strip() == "/tweet":
        # return a help message
        screen_name = twitter.token.get("screen_name", None)
        msg_html = render_template("bot_help_message.html", screen_name=screen_name)
        return jsonify({
            "message": msg_html,
            "message_format": "html",
        })

    # chop off the tweet command
    if message.startswith("/tweet "):
        message = message[7:]

    # time to actually tweet!
    resp = twitter.post("statuses/update.json", data={
        "status": message,
    })

    if not resp.ok:
        # tweeting failed
        current_app.logger.error(resp.text)
        # try to get the error message from Twitter
        try:
            result = resp.json()
            errors = [e["message"] for e in result["errors"]]
            if len(errors) == 1:
                reason = "Twitter says: {error}".format(error=errors[1])
            else:
                reason = "Twitter has {num} errors: {errors}".format(
                    num=len(errors), errors=", ".join(errors)
                )
        except Exception:
            reason = "Twitter isn't cooperating. :("
        return jsonify({
            "message": "(failed) Failed to tweet. " + reason,
            "message_format": "text",
        })

    # it worked! let's show off our new tweet
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

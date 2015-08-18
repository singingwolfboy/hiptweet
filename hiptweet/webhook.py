from flask import Blueprint, jsonify
from flask_login import login_required, current_user
from flask_dance.contrib.twitter import twitter
from hiptweet import db

webhook = Blueprint('webhook', __name__)


@webhook.route("/room_message", methods=["POST"])
@login_required
def room_message():
    return jsonify({
        "message": "You rang?",
        "message_format": "text",
    })

from flask import Blueprint, jsonify, url_for
from hiptweet import HIPCHAT_SCOPES

descriptors = Blueprint('descriptors', __name__)


@descriptors.route("/capabilities")
def capabilities():
    return jsonify({
        "name": "HipTweet",
        "description": "A HipChat bot that can tweet!",
        "key": "name.davidbaumgold.hiptweet",
        "links": {
            "homepage": "https://github.com/singingwolfboy/hiptweet",
            "self": url_for("descriptors.capabilities", _external=True),
        },
        "capabilities": {
            "hipchatApiConsumer": {
                "scopes": HIPCHAT_SCOPES,
            }
        },
        "configurable": {
            "url": url_for("ui.configure", _external=True),
        }
    })

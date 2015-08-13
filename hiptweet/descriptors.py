import json
from flask import Blueprint, jsonify, url_for, request
from hiptweet import HIPCHAT_SCOPES, db
from hiptweet.models import HipChatInstallInfo

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
                "fromName": "HipTweet",
            },
            "installable": {
                "allowRoom": True,
                "allowGlobal": True,
                "callbackUrl": url_for("descriptors.installed", _external=True)
            },
            "configurable": {
                "url": url_for("ui.configure", _external=True),
            },
        },
    })


@descriptors.route("/installed", methods=["POST"])
def installed():
    try:
        fields = json.loads(request.data.decode('utf-8'))
    except ValueError:
        return "invalid JSON", 400
    install_info = HipChatInstallInfo()
    install_info.oauth_id = fields.get("oauthId")
    install_info.oauth_secret = fields.get("oauthSecret")
    install_info.capabilities_url = fields.get("capabilitiesUrl")
    install_info.room_id = fields.get("roomId")
    db.session.add(install_info)
    db.session.commit()
    return "success"

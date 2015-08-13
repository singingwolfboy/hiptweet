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
    group_id = fields.get("groupId")
    if not group_id:
        return "missing groupId field", 400
    oauth_id = fields.get("oauthId")
    if not oauth_id:
        return "missing oauthId field", 400
    oauth_secret = fields.get("oauthSecret")
    if not oauth_secret:
        return "missing oauthSecret field", 400
    room_id = fields.get("roomId")  # optional

    # do we already have install info for this group/room combo?
    install_info = (
        HipChatInstallInfo.query
        .filter_by(group_id=group_id, room_id=room_id)
        .first()
    )
    # if not, make a new install info object
    if not install_info:
        install_info = HipChatInstallInfo(group_id=group_id, room_id=room_id)
    # update with OAuth credentials
    install_info.oauth_id = oauth_id
    install_info.oauth_secret = oauth_secret
    # save
    db.session.add(install_info)
    db.session.commit()
    # and we're done!
    return "success"

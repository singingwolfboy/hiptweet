import json
from flask import Blueprint, jsonify, url_for, request
from hiptweet import HIPCHAT_SCOPES, db
from hiptweet.models import HipChatGroup, HipChatInstallInfo, HipChatGroupOAuth
from .auth import Unauthorized, fetch_oauth_token

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
            "webhook": [
                {
                    "event": "room_message",
                    "url": url_for("webhook.room_message", _external=True),
                    "pattern": "^/tweet ?",
                    "authentication": "jwt",
                }
            ]
        },
    })


@descriptors.errorhandler(Unauthorized)
def handle_invalid_usage(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response



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
    capabilities_url = fields.get("capabilitiesUrl")
    if not capabilities_url:
        return "missing capabilitiesUrl field", 400
    room_id = fields.get("roomId")  # optional

    # validate the info we received
    token_data = fetch_oauth_token(capabilities_url, oauth_id, oauth_secret)

    # do we already have this HipChat group in the database?
    group = HipChatGroup.query.get(group_id)
    # if not, add it
    if not group:
        group = HipChatGroup(id=group_id)

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
    install_info.capabilities_url = capabilities_url
    install_info.oauth_id = oauth_id
    install_info.oauth_secret = oauth_secret

    # save the OAuth token we got
    token = HipChatGroupOAuth(install_info=install_info, token=token_data)

    # save
    db.session.add_all([group, install_info, token])
    db.session.commit()
    # and we're done!
    return "success"


@descriptors.route("/installed/<oauth_id>", methods=["DELETE"])
def uninstalled(oauth_id):
    install_info = HipChatInstallInfo.query.filter_by(oauth_id=oauth_id).first_or_404()
    # Verify the uninstall request. If this request really comes from HipChat,
    # we should be unable to request a new OAuth token.
    try:
        token_data = fetch_oauth_token(
            install_info.capabilities_url,
            install_info.oauth_id,
            install_info.oauth_secret,
        )
    except Unauthorized:
        # yep, we're unable to request a new token.
        db.session.delete(install_info)
        db.session.commit()
        return "goodbye"
    else:
        # actually, we can still get new tokens, so this is an invalid request.
        # might as well save the token we just got, though.
        (
            HipChatGroupOAuth.query.filter_by(install_info=install_info)
            .update({"token": token_data}, synchronize_session=False)
        )
        db.session.commit()
        return "invalid request", 403

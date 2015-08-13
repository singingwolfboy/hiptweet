import json
from flask import Blueprint, jsonify, url_for, request
import requests
from hiptweet import HIPCHAT_SCOPES, db
from hiptweet.models import HipChatGroup, HipChatInstallInfo, HipChatGroupOAuth

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
    capabilities_url = fields.get("capabilitiesUrl")
    if not capabilities_url:
        return "missing capabilitiesUrl field", 400
    room_id = fields.get("roomId")  # optional

    # validate the info we received
    capabilities_resp = requests.get(capabilities_url)
    if not capabilities_resp.ok:
        return "invalid capabilities URL", 400
    try:
        remote_capabilities = capabilities_resp.json()
    except ValueError:
        return "invalid JSON from capabilities URL", 400
    remote_app_name = remote_capabilities.get("name")
    if remote_app_name != "HipChat":
        msg = "expected remote app to be HipChat, received {name!r}".format(name=remote_app_name)
        return msg, 400

    # fetch an OAuth token
    token_url = (
        remote_capabilities.get("capabilities", {})
                           .get("oauth2Provider", {})
                           .get("tokenUrl", "")
    )
    if not token_url:
        return "tokenUrl not present in remote capabilities", 400
    payload = {
        "grant_type": "client_credentials",
        "scope": " ".join(HIPCHAT_SCOPES),
    }
    token_resp = requests.post(
        token_url,
        data=payload,
        auth=(oauth_id, oauth_secret),
    )
    if not token_resp.ok:
        return "could not obtain OAuth token", 400
    try:
        token_data = token_resp.json()
    except ValueError:
        return "invalid JSON from token URL", 400
    if "access_token" not in token_data:
        return "access_token not in token URL response", 400

    # OK, we're done validating things! Now time to save things.

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
    install_info.oauth_id = oauth_id
    install_info.oauth_secret = oauth_secret

    # save the OAuth token we got
    token = HipChatGroupOAuth(group_id=group_id, token=token_data)

    # save
    db.session.add_all([group, install_info, token])
    db.session.commit()
    # and we're done!
    return "success"


@descriptors.route("/installed/<oauth_id>", methods=["DELETE"])
def uninstalled(oauth_id):
    # delete the install info for this OAuth ID
    num_deleted = HipChatInstallInfo.query.filter_by(oauth_id=oauth_id).delete()
    return "goodbye"

import json
import itsdangerous
import requests
from hiptweet import HIPCHAT_SCOPES, db, login_manager
from hiptweet.models import User, HipChatUser, HipChatInstallInfo


@login_manager.request_loader
def load_user_from_request(request):
    jwt = request.args.get("signed_request")
    if jwt:
        headers_b64, payload_b64, signature = jwt.split(".")
        payload = json.loads(itsdangerous.base64_decode(payload_b64).decode('utf-8'))
        oauth_id = payload["iss"]
        install_info = HipChatInstallInfo.query.filter_by(oauth_id=oauth_id).first()
        if install_info:
            serializer = itsdangerous.JSONWebSignatureSerializer(install_info.oauth_secret)
            try:
                payload2 = serializer.loads(jwt)
            except itsdangerous.BadSignature:
                pass
            else:
                hc_user_id = payload2["prn"]
                hc_user = HipChatUser.query.get(hc_user_id)
                if not hc_user:
                    hc_user = HipChatUser(id=hc_user_id, group=install_info.group)
                    db.session.add(hc_user)
                    db.session.save()
                user = hc_user.user
                if not user:
                    user = User(hipchat_user=hc_user)
                    db.session.add(user)
                    db.session.save()
                return user
    return None


class Unauthorized(Exception):
    """
    http://flask.pocoo.org/docs/0.10/patterns/apierrors/
    """
    status_code = 400

    def __init__(self, message, status_code=None, payload=None):
        Exception.__init__(self)
        self.message = message
        if status_code is not None:
            self.status_code = status_code
        self.payload = payload

    def to_dict(self):
        rv = dict(self.payload or ())
        rv['message'] = self.message
        return rv


def fetch_oauth_token(capabilities_url, oauth_id, oauth_secret):
    capabilities_resp = requests.get(capabilities_url)
    if not capabilities_resp.ok:
        raise Unauthorized("invalid capabilities URL")
    try:
        remote_capabilities = capabilities_resp.json()
    except ValueError:
        raise Unauthorized("invalid JSON from capabilities URL")
    remote_app_name = remote_capabilities.get("name")
    if remote_app_name != "HipChat":
        msg = "expected remote app to be HipChat, received {name!r}".format(name=remote_app_name)
        raise Unauthorized(msg)

    # fetch an OAuth token
    token_url = (
        remote_capabilities.get("capabilities", {})
                           .get("oauth2Provider", {})
                           .get("tokenUrl", "")
    )
    if not token_url:
        raise Unauthorized("tokenUrl not present in remote capabilities")
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
        raise Unauthorized("could not obtain OAuth token")
    try:
        token_data = token_resp.json()
    except ValueError:
        raise Unauthorized("invalid JSON from token URL")
    if "access_token" not in token_data:
        raise Unauthorized("access_token not in token URL response")
    return token_data

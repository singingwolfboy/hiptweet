import os
from flask import Flask, jsonify, url_for
from werkzeug.contrib.fixers import ProxyFix
from flask_sslify import SSLify
from raven.contrib.flask import Sentry
from flask_dance.consumer import OAuth2ConsumerBlueprint

app = Flask(__name__)
app.wsgi_app = ProxyFix(app.wsgi_app)

envvars = (
    "HIPCHAT_OAUTH_CLIENT_ID", "HIPCHAT_OAUTH_CLIENT_SECRET",
    "SENTRY_DSN",
)
for envvar in envvars:
    app.config[envvar] = os.environ.get(envvar)

sentry = Sentry(app)
if not app.debug:
    SSLify(app)

hipchat_bp = OAuth2ConsumerBlueprint("hipchat", __name__,
    authorization_url="https://www.hipchat.com/users/authorize",
    token_url="https://api.hipchat.com/v2/oauth/token",
    base_url="https://api.hipchat.com/v2",
    scopes=["send_notification"],
)
hipchat_bp.from_config["client_id"] = "HIPCHAT_OAUTH_CLIENT_ID"
hipchat_bp.from_config["client_secret"] = "HIPCHAT_OAUTH_CLIENT_SECRET"
app.register_blueprint(hipchat_bp, url_prefix="/login")

@app.route("/")
def hello():
    return "this is hiptweet"

@app.route("/capabilities")
def capabilities():
    return jsonify({
        "name": "HipTweet",
        "description": "A HipChat bot that can tweet!",
        "key": "name.davidbaumgold.hiptweet",
        "links": {
            "homepage": "https://github.com/singingwolfboy/hiptweet",
            "self": url_for("capabilities", _external=True),
        },
        "capabilities": {
            "hipchatApiConsumer": {
                "scopes": [
                    "send_notification"
                ]
            }
        }
    })

if __name__ == "__main__":
    app.run()

import os
from flask import Flask, jsonify, url_for, render_template, request
from werkzeug.contrib.fixers import ProxyFix
from flask_sslify import SSLify
from raven.contrib.flask import Sentry
from flask_dance.consumer import OAuth2ConsumerBlueprint

app = Flask(__name__)
app.wsgi_app = ProxyFix(app.wsgi_app)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "supersekrit")

envvars = (
    "HIPCHAT_OAUTH_CLIENT_ID", "HIPCHAT_OAUTH_CLIENT_SECRET",
    "SENTRY_DSN",
)
for envvar in envvars:
    app.config[envvar] = os.environ.get(envvar)

sentry = Sentry(app)
if not app.debug:
    SSLify(app)

HIPCHAT_SCOPES = ["send_notification"]
hipchat_bp = OAuth2ConsumerBlueprint("hipchat", __name__,
    authorization_url="https://www.hipchat.com/users/authorize",
    token_url="https://api.hipchat.com/v2/oauth/token",
    base_url="https://api.hipchat.com/v2",
    scope=HIPCHAT_SCOPES,
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
                "scopes": HIPCHAT_SCOPES,
            }
        },
        "configurable": {
            "url": url_for("configure", _external=True),
        }
    })

@app.route("/configure")
def configure():
    jwt = request.args.get("signed_request")
    return render_template("configure.html", jwt=jwt)


if __name__ == "__main__":
    app.run()

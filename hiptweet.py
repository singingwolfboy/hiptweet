from flask import Flask, jsonify, url_for
from flask_sslify import SSLify

app = Flask(__name__)
if not app.debug:
    SSLify(app)

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

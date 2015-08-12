from flask import Blueprint, jsonify, url_for, request, render_template

ui = Blueprint('ui', __name__)

@ui.route("/")
def hello():
    return "this is hiptweet"

@ui.route("/configure")
def configure():
    jwt = request.args.get("signed_request")
    return render_template("configure.html", jwt=jwt)

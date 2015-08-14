from flask import Blueprint, jsonify, url_for, request, render_template
from flask_login import login_required
from .auth import load_user_from_request

ui = Blueprint('ui', __name__)

@ui.route("/")
def hello():
    return "this is hiptweet"

@ui.route("/configure")
@login_required
def configure():
    return render_template("configure.html")

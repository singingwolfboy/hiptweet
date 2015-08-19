from flask import Blueprint, jsonify, url_for, request, render_template, abort, flash
from flask_login import login_required, current_user
from hiptweet import db
from hiptweet.forms import GroupDefaultForm

ui = Blueprint('ui', __name__)

@ui.route("/")
def hello():
    return "this is hiptweet"

@ui.route("/configure")
@login_required
def configure():
    twitter_screen_names = [
        oauth.token.get("screen_name")
        for oauth in current_user.oauth_models
        if oauth.provider == "twitter" and oauth.token.get("screen_name")
    ]
    form = GroupDefaultForm()
    if form.validate_on_submit():
        group = current_user.hipchat_group
        group.twitter_oauth = form.oauth.data
        db.session.add(group)
        db.session.commit()
        flash("Group default updated!")
    return render_template(
        "configure.html",
        form=form,
        twitter_screen_names=twitter_screen_names,
    )


@ui.route("/twitter/<screen_name>", methods=["DELETE"])
@login_required
def delete_twitter_oauth_token(screen_name):
    oauth_models = [
        oauth for oauth in current_user.oauth_models
        if oauth.provider == "twitter"
        and oauth.token.get("screen_name") == screen_name
    ]
    if not oauth_models:
        abort(404)
    for oauth_model in oauth_models:
        db.session.delete(oauth_model)
    db.session.commit()
    return "", 204

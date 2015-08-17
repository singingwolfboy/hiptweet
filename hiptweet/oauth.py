from flask_dance.contrib.twitter import make_twitter_blueprint
from flask_dance.consumer.backend.sqla import SQLAlchemyBackend
from flask_dance.consumer import oauth_error
from flask import flash
from hiptweet import db
from hiptweet.models import OAuth
from flask_login import current_user


twitter_bp = make_twitter_blueprint(
    redirect_to="ui.configure",
    backend=SQLAlchemyBackend(OAuth, db.session, user=current_user)
)

# notify on OAuth provider error
@oauth_error.connect_via(twitter_bp)
def twitter_error(blueprint, response):
    msg = "Failed to authenticate with Twitter."
    flash(msg, category="error")

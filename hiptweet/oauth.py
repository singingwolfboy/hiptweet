from flask_dance.contrib.twitter import make_twitter_blueprint
from flask_dance.consumer.backend.sqla import SQLAlchemyBackend
from hiptweet import db
from hiptweet.models import OAuth
from flask_login import current_user


twitter_bp = make_twitter_blueprint(
    redirect_to="ui.configure",
    backend=SQLAlchemyBackend(OAuth, db.session, user=current_user)
)

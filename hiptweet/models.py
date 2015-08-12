from hiptweet import db
from flask_dance.consumer.backend.sqla import OAuthConsumerMixin


class OAuth(db.Model, OAuthConsumerMixin):
    pass

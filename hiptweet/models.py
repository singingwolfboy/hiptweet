from hiptweet import db
from flask_dance.consumer.backend.sqla import OAuthConsumerMixin


class OAuth(db.Model, OAuthConsumerMixin):
    pass


class HipChatInstallInfo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    capabilities_url = db.Column(db.String(512))
    client_id = db.Column(db.String(256), nullable=False)
    client_secret = db.Column(db.String(256), nullable=False)
    room_id = db.Column(db.String(256))

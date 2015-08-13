from hiptweet import db
from flask_dance.consumer.backend.sqla import OAuthConsumerMixin


class OAuth(db.Model, OAuthConsumerMixin):
    pass


class HipChatGroup(db.Model):
    __tablename__ = "hipchat_group"
    id = db.Column(db.Integer, primary_key=True)


class HipChatInstallInfo(db.Model):
    __tablename__ = "hipchat_install_info"
    id = db.Column(db.Integer, primary_key=True)
    group_id = db.Column(db.Integer, db.ForeignKey(HipChatGroup.id), nullable=False)
    group = db.relationship(HipChatGroup)
    room_id = db.Column(db.String(256))
    oauth_id = db.Column(db.String(256), nullable=False)
    oauth_secret = db.Column(db.String(256), nullable=False)

    __table_args__ = (
        # can't have multiple install infos for the same group,
        # unless they are for different rooms in the group
        db.UniqueConstraint(group_id, room_id),
    )

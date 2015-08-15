from datetime import datetime
from sqlalchemy.orm import backref
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.ext.mutable import MutableDict
from sqlalchemy_utils import JSONType
from flask_login import UserMixin
from flask_dance.consumer.backend.sqla import OAuthConsumerMixin
from hiptweet import db, login_manager


class HipChatGroup(db.Model):
    __tablename__ = "hipchat_group"
    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    # the columns below require the "view_group" scope to look up
    name = db.Column(db.String(256))
    avatar_url = db.Column(db.String(256))  # URL to group's avatar. 125px on the longest side.
    domain = db.Column(db.String(256))  # the Google Apps domain, if applicable
    subdomain = db.Column(db.String(256))  # the name used as the prefix to the HipChat domain


class HipChatUser(db.Model):
    __tablename__ = "hipchat_user"
    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    group_id = db.Column(db.Integer, db.ForeignKey(HipChatGroup.id), nullable=False)
    group = db.relationship(HipChatGroup, backref="users")
    # the columns below require the "view_group" scope to look up
    name = db.Column(db.String(256))
    title = db.Column(db.String(256))
    email = db.Column(db.String(256))
    photo_url = db.Column(db.String(256))  # URL to user's photo. 125px on the longest side.
    is_group_admin = db.Column(db.Boolean)
    is_guest = db.Column(db.Boolean)  # Whether or not this user is a guest or registered user.
    mention_name = db.Column(db.String(256))
    timezone = db.Column(db.String(64))
    xmpp_jid = db.Column(db.String(256))  # XMPP/Jabber ID of the user.


class HipChatInstallInfo(db.Model):
    __tablename__ = "hipchat_install_info"
    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    group_id = db.Column(db.Integer, db.ForeignKey(HipChatGroup.id), nullable=False)
    group = db.relationship(HipChatGroup)
    room_id = db.Column(db.String(256))
    capabilities_url = db.Column(db.String(512))
    oauth_id = db.Column(db.String(256), nullable=False, index=True)
    oauth_secret = db.Column(db.String(256), nullable=False)

    __table_args__ = (
        # can't have multiple install infos for the same group,
        # unless they are for different rooms in the group
        db.UniqueConstraint(group_id, room_id),
    )


class HipChatGroupOAuth(db.Model):
    __tablename__ = "hipchat_group_oauth"
    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    install_info_id = db.Column(db.Integer,
        db.ForeignKey(HipChatInstallInfo.id, ondelete="CASCADE"),
        nullable=False,
    )
    install_info = db.relationship(HipChatInstallInfo)
    token = db.Column(MutableDict.as_mutable(JSONType))

    @classmethod
    def for_group(cls, group_id, room_id=None):
        return (
            cls.query.join(HipChatInstallInfo)
            .filter(HipChatInstallInfo.group_id == group_id)
            .filter(HipChatInstallInfo.room_id == room_id)
            .first()
        )


class User(db.Model, UserMixin):
    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    hipchat_user_id = db.Column(
        db.Integer, db.ForeignKey(HipChatUser.id), nullable=False, index=True,
    )
    hipchat_user = db.relationship(
        HipChatUser, backref=backref("user", uselist=False),
    )
    hipchat_group = association_proxy("hipchat_user", "group")


@login_manager.user_loader
def load_user(userid):
    return User.get(userid)


class OAuth(db.Model, OAuthConsumerMixin):
    user_id = db.Column(db.Integer, db.ForeignKey(User.id))
    user = db.relationship(User, backref="oauth_models")

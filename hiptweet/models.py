from datetime import datetime
from sqlalchemy.orm import backref
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.ext.mutable import MutableDict
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm.collections import attribute_mapped_collection
from sqlalchemy_utils import JSONType
from flask_login import UserMixin
from flask_dance.consumer.backend.sqla import OAuthConsumerMixin
from hiptweet import db, login_manager


class TimestampMixin(object):
    """
    Adds some basic timestamps to this model.
    """
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)


class HipChatGroup(db.Model, TimestampMixin):
    __tablename__ = "hipchat_group"
    id = db.Column(db.Integer, primary_key=True)
    twitter_oauth_id = db.Column(
        db.Integer,
        db.ForeignKey("oauth.id", name="FK_HIPCHATGROUP_OAUTH"),
    )
    twitter_oauth = db.relationship("OAuth")
    # the columns below require the "view_group" scope to look up
    name = db.Column(db.String(256))
    avatar_url = db.Column(db.String(256))  # URL to group's avatar. 125px on the longest side.
    domain = db.Column(db.String(256))  # the Google Apps domain, if applicable
    subdomain = db.Column(db.String(256))  # the name used as the prefix to the HipChat domain

    @hybrid_property
    def twitter_oauths(self):
        """
        returns all OAuth objects associated with this group
        """
        return (OAuth.query
            .join(User)
            .join(HipChatUser)
            .filter(HipChatUser.group_id == self.id)
        )

    def __repr__(self):
        parts = []
        parts.append(self.__class__.__name__)
        if self.name:
            parts.append('name="{}"'.format(self.name))
        if self.id:
            parts.append("id={}".format(self.id))
        return "<{}>".format(" ".join(parts))


class HipChatUser(db.Model, TimestampMixin):
    __tablename__ = "hipchat_user"
    id = db.Column(db.Integer, primary_key=True)
    group_id = db.Column(
        db.Integer,
        db.ForeignKey(HipChatGroup.id, name="FK_HIPCHATUSER_HIPCHATGROUP"),
        nullable=False,
    )
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

    def __repr__(self):
        parts = []
        parts.append(self.__class__.__name__)
        if self.name:
            parts.append('name="{}"'.format(self.name))
        if self.id:
            parts.append("id={}".format(self.id))
        return "<{}>".format(" ".join(parts))


class HipChatRoom(db.Model, TimestampMixin):
    __tablename__ = "hipchat_room"
    id = db.Column(db.Integer, primary_key=True)
    group_id = db.Column(db.Integer, db.ForeignKey(HipChatGroup.id), nullable=False)
    group = db.relationship(HipChatGroup, backref="rooms")
    twitter_oauth_id = db.Column(db.Integer, db.ForeignKey("oauth.id"))
    twitter_oauth = db.relationship("OAuth")
    # the columns below require the "view_group" or "view_room" scope to look up
    name = db.Column(db.String(256))
    topic = db.Column(db.String(256))
    privacy = db.Column(db.String(64))  # Privacy setting: "public" or "private"
    avatar_url = db.Column(db.String(256))  # URL to room's avatar. 125px on the longest side.
    is_archived = db.Column(db.Boolean)
    is_guest_accessible = db.Column(db.Boolean)  # Whether or not guests can access this room.
    owner_id = db.Column(db.Integer, db.ForeignKey(HipChatUser.id))
    owner = db.relationship(HipChatUser, backref="owned_rooms")
    xmpp_jid = db.Column(db.String(256))  # XMPP/Jabber ID of the room.

    def __repr__(self):
        parts = []
        parts.append(self.__class__.__name__)
        if self.name:
            parts.append('name="{}"'.format(self.name))
        if self.id:
            parts.append("id={}".format(self.id))
        return "<{}>".format(" ".join(parts))


class HipChatInstallInfo(db.Model, TimestampMixin):
    __tablename__ = "hipchat_install_info"
    id = db.Column(db.Integer, primary_key=True)
    group_id = db.Column(db.Integer, db.ForeignKey(HipChatGroup.id), nullable=False)
    group = db.relationship(HipChatGroup, backref="install_info")
    room_id = db.Column(db.Integer, db.ForeignKey(HipChatRoom.id), nullable=True)
    room = db.relationship(HipChatRoom)
    capabilities_url = db.Column(db.String(512))
    oauth_id = db.Column(db.String(256), nullable=False, index=True)
    oauth_secret = db.Column(db.String(256), nullable=False)
    tokens = association_proxy("oauth_models", "token")

    __table_args__ = (
        # can't have multiple install infos for the same group,
        # unless they are for different rooms in the group
        db.UniqueConstraint(group_id, room_id),
    )

    def __repr__(self):
        parts = []
        parts.append(self.__class__.__name__)
        if self.group.name:
            parts.append('group="{}"'.format(self.group.name))
        else:
            parts.append('group_id={}'.format(self.group.id))
        if self.room_id:
            if self.room.name:
                parts.append('room="{}"'.format(self.room.name))
            else:
                parts.append('room_id={}'.format(self.room.id))
        if self.oauth_id:
            parts.append('oauth_id="{}"'.format(self.oauth_id))
        return "<{}>".format(" ".join(parts))


class HipChatGroupOAuth(db.Model, TimestampMixin):
    __tablename__ = "hipchat_group_oauth"
    id = db.Column(db.Integer, primary_key=True)
    install_info_id = db.Column(db.Integer,
        db.ForeignKey(HipChatInstallInfo.id, ondelete="CASCADE"),
        nullable=False,
    )
    install_info = db.relationship(
        HipChatInstallInfo,
        cascade="all, delete-orphan",
        single_parent=True,
        backref="oauth_models"
    )
    token = db.Column(MutableDict.as_mutable(JSONType))

    @classmethod
    def for_group(cls, group_id, room_id=None):
        return (
            cls.query.join(HipChatInstallInfo)
            .filter(HipChatInstallInfo.group_id == group_id)
            .filter(HipChatInstallInfo.room_id == room_id)
            .first()
        )

    def __repr__(self):
        parts = []
        parts.append(self.__class__.__name__)
        parts.append(repr(self.install_info))
        return "<{}>".format(" ".join(parts))


class User(db.Model, TimestampMixin, UserMixin):
    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key=True)
    hipchat_user_id = db.Column(
        db.Integer,
        db.ForeignKey(HipChatUser.id, name="FK_USER_HIPCHATUSER"),
        nullable=False,
        index=True,
    )
    hipchat_user = db.relationship(
        HipChatUser, backref=backref("user", uselist=False),
    )
    hipchat_group = association_proxy("hipchat_user", "group")

    def __repr__(self):
        parts = []
        parts.append(self.__class__.__name__)
        if self.hipchat_user.name:
            parts.append('name="{}"'.format(self.hipchat_user.name))
        else:
            parts.append('hichat_user_id={}'.format(self.hipchat_user.id))
        if self.id:
            parts.append("id={}".format(self.id))
        return "<{}>".format(" ".join(parts))


@login_manager.user_loader
def load_user(userid):
    return User.query.get(userid)


class OAuth(db.Model, OAuthConsumerMixin):
    __tablename__ = "oauth"
    user_id = db.Column(
        db.Integer,
        db.ForeignKey(User.id, name="FK_OAUTH_USER"),
    )
    user = db.relationship(User, backref="oauth_models")


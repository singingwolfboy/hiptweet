from datetime import datetime
from sqlalchemy.ext.mutable import MutableDict
from sqlalchemy_utils import JSONType
from hiptweet import db


class HipChatGroup(db.Model):
    __tablename__ = "hipchat_group"
    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    # the columns below require the "view_group" scope to determine
    name = db.Column(db.String(256))
    avatar_url = db.Column(db.String(256))  # URL to group's avatar. 125px on the longest side.
    domain = db.Column(db.String(256))  # the Google Apps domain, if applicable
    subdomain = db.Column(db.String(256))  # the name used as the prefix to the HipChat domain


class HipChatInstallInfo(db.Model):
    __tablename__ = "hipchat_install_info"
    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    group_id = db.Column(db.Integer, db.ForeignKey(HipChatGroup.id), nullable=False)
    group = db.relationship(HipChatGroup)
    room_id = db.Column(db.String(256))
    capabilities_url = db.Column(db.String(512))
    oauth_id = db.Column(db.String(256), nullable=False)
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

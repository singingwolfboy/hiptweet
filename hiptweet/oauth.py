from flask_dance.contrib.twitter import make_twitter_blueprint
from flask_dance.consumer.backend import BaseBackend
from flask_dance.consumer import oauth_error
from flask import flash
from hiptweet import db
from hiptweet.models import User, OAuth, HipChatRoom, HipChatGroup
from flask_login import current_user


class HipChatGroupAssocationBackend(BaseBackend):
    def _get_room_and_group(self, blueprint):
        room = blueprint.config.get("room")
        if not room:
            room_id = blueprint.config.get("room_id")
            if room_id:
                room = HipChatRoom.query.get(room_id)
        if room:
            return room, room.group

        group = blueprint.config.get("group")
        if not group:
            group_id = blueprint.config.get("group_id")
            if group_id:
                group = HipChatGroup.query.get(group_id)
        # if we still haven't found a group, use the group of the logged in user
        if not group:
            group = current_user.hipchat_group

        return None, group

    def get(self, blueprint):
        room, group = self._get_room_and_group(blueprint)
        attrname = "{name}_oauth".format(name=blueprint.name)
        oauth_model = getattr(room, attrname, None) or getattr(group, attrname, None)
        return getattr(oauth_model, "token", {})

    def set(self, blueprint, token):
        user = blueprint.config.get("user")
        if not user:
            user_id = blueprint.config.get("user_id")
            if user_id:
                user = User.query.get(user_id)
        if not user:
            user = current_user._get_current_object()

        oauth_model = OAuth(
            provider=blueprint.name,
            token=token,
            user=user,
        )
        db.session.add(oauth_model)

        # if this is the first OAuth model we're creating for the group,
        # make it the default.
        group = user.hipchat_group
        if group.twitter_oauths.count() == 0:
            group.twitter_oauth = oauth_model
            db.session.add(group)

        db.session.commit()

    def delete(self, blueprint, user=None, user_id=None):
        room, group = self._get_room_and_group(blueprint)
        attrname = "{name}_oauth".format(name=blueprint.name)
        oauth_model = getattr(room, attrname, None) or getattr(group, attrname, None)
        if oauth_model:
            db.session.delete(oauth_model)
        db.session.commit()


twitter_bp = make_twitter_blueprint(
    redirect_to="ui.configure",
    backend=HipChatGroupAssocationBackend(),
)

# notify on OAuth provider error
@oauth_error.connect_via(twitter_bp)
def twitter_error(blueprint, response):
    msg = "Failed to authenticate with Twitter."
    flash(msg, category="error")

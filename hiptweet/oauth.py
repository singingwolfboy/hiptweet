from flask_dance.contrib.twitter import make_twitter_blueprint
from flask_dance.consumer.backend import BaseBackend
from flask_dance.consumer import oauth_authorized, oauth_error
from flask import flash, current_app
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

        # count the number of oauth models we currently have for this group
        group = user.hipchat_group
        num_connections = group.twitter_oauths.count()
        current_app.logger.info(
            "num_connections for %(group)s = %(num)s",
            group=group,
            num=num_connections,
        )

        # make the new model
        oauth_model = OAuth(
            provider=blueprint.name,
            token=token,
            user=user,
        )
        db.session.add(oauth_model)

        # if this is the first model for this group, make it the default
        if num_connections == 0:
            group.twitter_oauth = oauth_model
            db.session.add(group)

        db.session.commit()

    def delete(self, blueprint, user=None, user_id=None):
        room, group = self._get_room_and_group(blueprint)
        attrname = "{name}_oauth".format(name=blueprint.name)
        oauth_model = getattr(room, attrname, None) or getattr(group, attrname, None)
        if oauth_model:
            db.session.delete(oauth_model)

        # if there's only one oauth model left for this group,
        # make it the default
        group = user.hipchat_group
        num_connections = group.twitter_oauths.count()
        current_app.logger.info(
            "num_connections for %(group)s = %(num)s",
            group=group,
            num=num_connections,
        )
        if num_connections == 1:
            group.twitter_oauth = group.twitter_oauths.first()
            db.session.add(group)

        db.session.commit()


twitter_bp = make_twitter_blueprint(
    redirect_to="ui.configure",
    backend=HipChatGroupAssocationBackend(),
)


@oauth_authorized.connect_via(twitter_bp)
def twitter_authorized(blueprint, token):
    pass


# notify on OAuth provider error
@oauth_error.connect_via(twitter_bp)
def twitter_error(blueprint, response):
    msg = "Failed to authenticate with Twitter."
    flash(msg, category="error")


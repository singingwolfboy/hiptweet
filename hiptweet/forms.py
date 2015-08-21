from flask_wtf import Form
from wtforms.ext.sqlalchemy.fields import QuerySelectField
from flask_login import current_user
from hiptweet.models import OAuth, User, HipChatUser, HipChatGroup


def oauth_models_for_group_of_current_user():
    return (OAuth.query
        .join(User)
        .join(HipChatUser)
        .join(HipChatGroup)
        .filter(HipChatUser.id == current_user.hipchat_user_id)
    )


def get_screen_name_from_oauth_model(model):
    return "@{sn}".format(sn=model.token["screen_name"])


class GroupDefaultForm(Form):
    oauth = QuerySelectField(
        'Default Twitter account',
        query_factory=oauth_models_for_group_of_current_user,
        default=lambda: current_user.hipchat_group.twitter_oauth,
        get_label=get_screen_name_from_oauth_model,
    )

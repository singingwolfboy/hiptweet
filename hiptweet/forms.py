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
    return model.token["screen_name"]


class GroupDefaultForm(Form):
    oauth = QuerySelectField(
        'Group Default',
        query_factory=oauth_models_for_group_of_current_user,
        get_label=get_screen_name_from_oauth_model,
        allow_blank=True,
    )

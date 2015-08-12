from flask_dance.consumer import OAuth2ConsumerBlueprint
from flask_dance.consumer.backend.sqla import SQLAlchemyBackend
from hiptweet import HIPCHAT_SCOPES
from hiptweet.models import db, OAuth


hipchat_bp = OAuth2ConsumerBlueprint("hipchat", __name__,
    authorization_url="https://www.hipchat.com/users/authorize",
    token_url="https://api.hipchat.com/v2/oauth/token",
    base_url="https://api.hipchat.com/v2",
    scope=HIPCHAT_SCOPES,
    backend=SQLAlchemyBackend(OAuth, db.session),
)
hipchat_bp.from_config["client_id"] = "HIPCHAT_OAUTH_CLIENT_ID"
hipchat_bp.from_config["client_secret"] = "HIPCHAT_OAUTH_CLIENT_SECRET"

import os


class DefaultConfig(object):
    SECRET_KEY = os.environ.get("FLASK_SECRET_KEY", "supersekrit")
    SENTRY_DSN = os.environ.get("SENTRY_DSN")
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL", "sqlite:///hiptweet.db")
    HIPCHAT_OAUTH_CLIENT_ID = os.environ.get("HIPCHAT_OAUTH_CLIENT_ID")
    HIPCHAT_OAUTH_CLIENT_SECRET = os.environ.get("HIPCHAT_OAUTH_CLIENT_SECRET")


class DevelopmentConfig(DefaultConfig):
    DEBUG = True

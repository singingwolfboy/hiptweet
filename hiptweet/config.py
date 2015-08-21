import os


class DefaultConfig(object):
    SECRET_KEY = os.environ.get("FLASK_SECRET_KEY", "supersekrit")
    SENTRY_DSN = os.environ.get("SENTRY_DSN")
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL", "sqlite:///hiptweet.db")
    TWITTER_OAUTH_API_KEY = os.environ.get("TWITTER_OAUTH_API_KEY")
    TWITTER_OAUTH_API_SECRET = os.environ.get("TWITTER_OAUTH_API_SECRET")
    CELERY_BROKER_URL = os.environ.get("RABBITMQ_BIGWIG_TX_URL", "amqp://")
    CELERY_ACCEPT_CONTENT = ["json"]
    CELERY_TASK_SERIALIZER = "json"
    CELERY_RESULT_SERIALIZER = "json"


class WorkerConfig(DefaultConfig):
    CELERY_BROKER_URL = os.environ.get("RABBITMQ_BIGWIG_RX_URL", "amqp://")


class DevelopmentConfig(DefaultConfig):
    DEBUG = True

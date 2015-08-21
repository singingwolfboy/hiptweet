import os
import sys
import logging
from flask import Flask
from werkzeug.contrib.fixers import ProxyFix
from hiptweet.middleware import HTTPMethodOverrideMiddleware
from raven.contrib.flask import Sentry
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_sslify import SSLify


HIPCHAT_SCOPES = ["send_notification"]


sentry = Sentry()
db = SQLAlchemy()
login_manager = LoginManager()


def expand_config(name):
    if not name:
        name = "default"
    return "hiptweet.config.{classname}Config".format(classname=name.capitalize())


def configure_logger(app):
    stderr_handler = logging.StreamHandler(sys.stderr)
    stderr_handler.setLevel(logging.INFO)
    app.logger.addHandler(stderr_handler)
    return app


def create_app(config=None):
    app = Flask(__name__)
    app.wsgi_app = ProxyFix(app.wsgi_app)
    app.wsgi_app = HTTPMethodOverrideMiddleware(app.wsgi_app, querystring_param="_method")
    config = config or os.environ.get("HIPTWEET_CONFIG") or "default"
    app.config.from_object(expand_config(config))

    configure_logger(app)
    sentry.init_app(app)
    db.init_app(app)
    login_manager.init_app(app)
    if not app.debug:
        SSLify(app)

    from .oauth import twitter_bp
    app.register_blueprint(twitter_bp, url_prefix="/login")

    from .descriptors import descriptors as descriptors_blueprint
    app.register_blueprint(descriptors_blueprint)

    from .ui import ui as ui_blueprint
    app.register_blueprint(ui_blueprint)

    from .webhook import webhook as webhook_blueprint
    app.register_blueprint(webhook_blueprint, url_prefix="/webhook")

    return app

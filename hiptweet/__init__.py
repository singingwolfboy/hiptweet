import os
from flask import Flask
from werkzeug.contrib.fixers import ProxyFix
from flask_sqlalchemy import SQLAlchemy
from flask_sslify import SSLify
from raven.contrib.flask import Sentry


HIPCHAT_SCOPES = ["send_notification"]


db = SQLAlchemy()
sentry = Sentry()


def expand_config(name):
    if not name:
        name = "default"
    return "hiptweet.config.{classname}Config".format(classname=name.capitalize())


def create_app(config=None):
    app = Flask(__name__)
    app.wsgi_app = ProxyFix(app.wsgi_app)
    config = config or os.environ.get("HIPTWEET_CONFIG") or "default"
    app.config.from_object(expand_config(config))

    sentry.init_app(app)
    db.init_app(app)
    if not app.debug:
        SSLify(app)

    from .oauth import hipchat_bp
    app.register_blueprint(hipchat_bp, url_prefix="/login")

    from .descriptors import descriptors as descriptors_blueprint
    app.register_blueprint(descriptors_blueprint)

    from .ui import ui as ui_blueprint
    app.register_blueprint(ui_blueprint)

    return app

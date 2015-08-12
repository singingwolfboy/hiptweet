#!/usr/bin/env python
from flask_script import Manager, prompt_bool
from hiptweet import create_app, db

manager = Manager(create_app)
manager.add_option('-c', '--config', dest='config', required=False)


@manager.command
def dbcreate():
    "Creates database tables from SQLAlchemy models"
    db.create_all()
    db.session.commit()


@manager.command
def dbdrop():
    "Drops database tables"
    if prompt_bool("Are you sure you want to lose all your data"):
        db.drop_all()
        db.session.commit()


if __name__ == "__main__":
    manager.run()

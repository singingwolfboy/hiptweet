#!/usr/bin/env python
from flask_script import Manager, prompt_bool
from hiptweet import create_app, db
import sqlalchemy as sa

manager = Manager(create_app)
manager.add_option('-c', '--config', dest='config', required=False)


dbmanager = Manager(usage="Perform database operations")

@dbmanager.command
def create():
    "Creates database tables from SQLAlchemy models"
    db.create_all()
    db.session.commit()


@dbmanager.command
def drop():
    "Drops database tables"
    if prompt_bool("Are you sure you want to lose all your data"):
        db.drop_all()
        db.session.commit()

@dbmanager.command
def sql():
    "Dumps SQL for creating database tables"
    def dump(sql, *multiparams, **params):
        if not isinstance(sql, basestring):
            sql = sql.compile(dialect=engine.dialect)
        print(sql)
    engine = sa.create_engine('postgresql://', strategy='mock', executor=dump)
    db.metadata.create_all(engine, checkfirst=False)

manager.add_command("db", dbmanager)

if __name__ == "__main__":
    manager.run()

#!/usr/bin/env python
from flask_script import Manager, prompt_bool
from hiptweet import app

manager = Manager(app)


if __name__ == "__main__":
    manager.run()

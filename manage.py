from flask_script import Manager
from flaskberry import app

manager = Manager(app)


@manager.command
def populate():
    from flaskberry.populate_db import populate_database
    print('Populating!')
    populate_database()
    print('Done!')


if __name__ == '__main__':
    manager.run()

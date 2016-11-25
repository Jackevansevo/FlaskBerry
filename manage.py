from flask_script import Manager, Command
from flaskberry import app

from flaskberry.populate_db import populate_database

import sys
import subprocess

manager = Manager(app)


class PopulateDatabase(Command):
    """Populates the database with sample data"""
    name = 'populate'

    def run(self):
        print('Populating!')
        populate_database()
        print('Done!')


class CeleryWorker(Command):
    """Starts the celery worker"""
    name = 'celery worker'
    capture_all_args = True

    def run(self, argv):
        ret = subprocess.call(
            ['celery', 'worker', '-A', 'flaskberry.celery'] + argv
        )
        sys.exit(ret)


class CeleryBeat(Command):
    """Starts the celery broker"""
    name = 'celery beat'
    capture_all_args = True

    def run(self, argv):
        ret = subprocess.call(
            ['celery', 'beat', '-A', 'flaskberry.celery'] + argv
        )
        sys.exit(ret)


manager.add_command("populate", PopulateDatabase())
manager.add_command("celery", CeleryWorker())
manager.add_command("beat", CeleryBeat())


if __name__ == '__main__':
    manager.run()

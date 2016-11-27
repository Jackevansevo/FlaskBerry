from flask import Flask
from celery import Celery

from flask_bcrypt import Bcrypt
from flask_mail import Mail
from flask_login import LoginManager

from pony.orm import Database, db_session

import os

basedir = os.path.abspath(os.path.dirname(__file__))

# Set up Flask application from config.py
app = Flask(__name__)
app.wsgi_app = db_session(app.wsgi_app)
app.config.from_object('config')

# Initialize Database connection
db = Database()

# Create the database file if it doesn't already exist
db.bind('postgres', user='', password='', host='', database='flaskberry')

# Set up bcrypt
bcrypt = Bcrypt(app)

# Set up Flask Mail
mail = Mail(app)

# Set up celery
celery = Celery(app.name, broker=app.config['CELERY_BROKER_URL'])
celery.conf.update(app.config)

# Import celery periodic tasks so they're registered with workers
from .tasks import setup_periodic_tasks # noqa


# Setup Login Manager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.session_protection = "strong"
login_manager.login_view = "login"


from . import views # noqa

db.generate_mapping(create_tables=True)

from flask import Flask
from pony.orm import Database, db_session
from flask_bcrypt import Bcrypt
import os

basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.wsgi_app = db_session(app.wsgi_app)
app.config.from_object('config')
bcrypt = Bcrypt(app)


db = Database()

# Create the database file if it doesn't already exist
db.bind('sqlite', os.path.join(basedir, 'db.sqlite'), create_db=True)

from flaskberry import views

db.generate_mapping(create_tables=True)

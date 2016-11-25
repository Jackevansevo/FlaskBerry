# FlaskBerry

Simple library software built using:
- Flask
- Tachyons
- Pony ORM

*Still very much WIP*


## Install Dependencies

    virtualenv -p path/to/python/installation venv
    source venv/bin/activate
    pip install -r requirements.txt

## Setup Environment

First populate the database

    python manage.py populate_db.py

In three separate terminals, run:

    python manage.py beat
    python manage.py celery
    python manage.py runserver


The loglevel flag can be passed to celery to aid debugging: 

    python manage.py celery --loglevel=info

Then visit: [http://localhost:5000/](http://localhost:5000/)


## Screenshot

![screenshot](screenshot.png "Screenshot")

from models import db, Customer, add_book_copy
from pony import orm
from collections import namedtuple
from faker import Factory as FakerFactory

import os

# Set up faker object
faker = FakerFactory.create('en_GB')


try:
    os.remove('db.sqlite')
except OSError:
    pass


# Create the database file if it doesn't already exist
db.bind('sqlite', 'db.sqlite', create_db=True)

# Create the tables if they do not already exist
db.generate_mapping(create_tables=True)

# Use debug mode to inspect SQL commands Pony sends to the database
# orm.sql_debug(True)


BookTuple = namedtuple('Book', 'title genre isbn')

books = (
    '1491946008',  '1633430235', '1593275919', '0545582970', '0545582970',
    '1593272812', '1593272952', '1473541875', '0575104422', '9781448190690',
    '0199678111', '1473642698', '0007557884', '1782391207', '0307346609',
    '1312792566', '0307827828', '1435238125'
)

# Commit changes inside a transaction
with orm.db_session:

    # Create some Sample customers
    for i in range(1, 5):
        Customer(forename=faker.first_name(), surname=faker.last_name())

    # Create some sample books
    [add_book_copy(isbn) for isbn in books]

    orm.commit()

from models import db, Customer, Book
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
orm.sql_debug(True)


BookTuple = namedtuple('Book', 'title genre isbn')

books = ('1491946008',  '1633430235', '1593275919', '0545582970')


# Commit changes inside a transaction
with orm.db_session:

    # Create some Sample customers
    for i in range(1, 5):
        Customer(forename=faker.first_name(), surname=faker.last_name())

    # Create some sample books
    for isbn in books:
        Book(isbn=isbn)

    orm.commit()

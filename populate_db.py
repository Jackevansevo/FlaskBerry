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

books = (
    BookTuple('Flask Web Development', 'Programming', '1449372627'),
    BookTuple('Clojure for the Brave and True', 'Programming', '1593275919'),
    BookTuple('Clojure Programming', 'Programming', '1449335349'),
    BookTuple('The Hobbit', 'Fiction', '0547951973'),
    BookTuple('The Catcher In the Rye', 'Fiction', '3526523711'),
    BookTuple('The Girl on the Train', 'Fiction', '0552779776'),
    BookTuple('A Brief History of Time', 'Science', '0593060504'),
)

# Commit changes inside a transaction
with orm.db_session:

    # Create some Sample customers
    for i in range(1, 20):
        Customer(forename=faker.first_name(), surname=faker.last_name())

    # Create some sample books
    for book in books:
        Book(**book._asdict())

    orm.commit()

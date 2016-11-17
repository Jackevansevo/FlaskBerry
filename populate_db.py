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
    BookTuple('C Programming Language', 'Programming', '0133086216'),
    BookTuple('C in a Nutshell', 'Programming', '0596550715'),
    BookTuple('Clojure Programming', 'Programming', '1449335349'),
    BookTuple('Clojure for the Brave and True', 'Programming', '1593275919'),
    BookTuple('Flask Web Development', 'Programming', '1449372627'),
    BookTuple('Go In Action', 'Programming', '1617291781'),
    BookTuple('The Go Programming Language', 'Programming', '0134190564'),
    BookTuple('Amazon Web Services in Action', 'Programming', '1617292885'),
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

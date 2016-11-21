from faker import Factory as FakerFactory
from flaskberry import db
from flaskberry.models import Customer, add_book_copy
from pony.orm import db_session, commit

# Set up faker object
faker = FakerFactory.create('en_GB')

books = (
    '1491946008',  '1633430235', '1593275919', '0545582970', '0545582970',
    '1593272812', '1593272952', '1473541875', '0575104422', '9781448190690',
    '0199678111', '1473642698', '0007557884', '1782391207', '0307346609',
    '1312792566', '0307827828', '1435238125'
)


def populate_database():
    db.drop_all_tables(with_all_data=True)
    db.create_tables()
    add_data()


@db_session
def add_data():
    # Create some Sample customers
    for i in range(1, 5):
        Customer(
            forename=faker.first_name(), surname=faker.last_name(),
            email=faker.email(), password=faker.password()
        )

    # Create some sample books
    [add_book_copy(isbn) for isbn in books]

    commit()

from faker import Factory as FakerFactory
from flaskberry import db
from flaskberry.models import Customer, add_book_copy
from pony.orm import db_session, commit
from flaskberry.isbn import to_isbn13

# Set up faker object
faker = FakerFactory.create('en_GB')


books = (
    # No Starch Press
    '9781593272074', '9781593271749', '9781593273842', '9781593275990',
    '9781593272067', '9781593271473', '9781593276515', '9781593272944',
    '9781593275754', '9781593277499', '9781593276492', '9781593274085',
    '9781593273897', '9781593274870', '9781593270773', '9781593275204',
    '9781593275402', '9781593276034', '9781593274078', '9781593276041',
    '9781593275723', '9781593274917', '9781593271480', '9781593275273',
    '9781593275662', '9781593277628', '9781593276126', '9781593270476',
    '9781593274245', '9781593273972', '9781593270612', '9781593270629',
    '9781593271732', '9781593271824', '9781593270124', '9781593270032',
    '9781593270568', '9781593272814', '9781593275914', '9781593274351',
    '9781593272838',
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
            email=faker.email(), password=b'test'
        )
    Customer(
        forename="Jack", surname="Evans", email="jack@evans.gb.net",
        password=b'test'
    )

    # Create some sample books
    [add_book_copy(isbn=to_isbn13(isbn)) for isbn in books]

    commit()

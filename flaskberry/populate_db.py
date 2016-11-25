from faker import Factory as FakerFactory
from flaskberry import db
from flaskberry.models import Customer, add_book_copy
from pony.orm import db_session, commit
from flaskberry.isbn import to_isbn13

# Set up faker object
faker = FakerFactory.create('en_GB')

# # Random Shite
# '9780552551052', '9781250081216', '9780307958044', '9781594203985',
# '9781503944435', '9780134190440', '9781491950357', '9781435238121',
# '9781617291784', '9781312792562', '9780307827821', '9781782391203',
# '9780307346605', '9780007557882', '9780199678112', '9781473642690',
# '9780575104426', '9781448190690', '9781593272951', '9780545582971',
# '9781593272814', '9781633430235', '9781593275914', '9781491946008',

books = (

    # Terry Prachet
    '0552166596', '055216660X', '0552166618', '0552166626', '0552166634',
    '0552166642', '0552166650', '0552166669', '1857989546', '0552166677',
    '0552166685', '0552167509', '0552167517',

    # Programming Books
    '9781593275914', '9780134190563', '9781491946251', '9781449357351',
    '9781491950319', '9781449319793', '9780596517748'

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
        forename="jack", surname="evans", email="jack@evans.gb.net",
        password=b'test'
    )

    # Create some sample books
    [add_book_copy(isbn=to_isbn13(isbn)) for isbn in books]

    commit()

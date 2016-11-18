from pony import orm
from flask import url_for
from datetime import date

# [TODO] Figure out a better slugify strategy
from slugify import UniqueSlugify
from scrape_info import fetch_json


# Establish Databse connection
db = orm.Database()

# Create UniqueSlugify instance to generate slugs
slugify = UniqueSlugify(to_lower=True)


class Customer(db.Entity):
    forename = orm.Required(str)
    surname = orm.Required(str)
    slug = orm.Optional(str, unique=True)
    books = orm.Set('Book')

    def before_insert(self):
        self.slug = slugify(str(self))

    def __str__(self):
        return ', '.join([self.forename, self.surname])


class Book(db.Entity):
    title = orm.Optional(str)
    subtitle = orm.Optional(str)
    genre = orm.Optional(str)
    isbn = orm.Optional(str)
    lender = orm.Optional(Customer)
    slug = orm.Optional(str, unique=True)

    authors = orm.Set('Author')
    loans = orm.Set('Loan')
    reviews = orm.Set('Review')

    def available(self):
        # Returns True if book is available
        if self.loans:
            return 'Unavailable'
        else:
            return 'Available'

    @property
    def author_names(self):
        return ", ".join(author.name for author in self.authors)

    @property
    def img(self):
        return 'http://images.amazon.com/images/P/' + self.isbn

    def before_insert(self):
        if self.isbn:
            populate_fields(self)
        self.slug = slugify(self.title)

    @property
    def url(self):
        return url_for('book', slug=self.slug)

    def __str__(self):
        return self.title


class Loan(db.Entity):
    start_date = orm.Required(date)
    end_date = orm.Required(date)
    book = orm.Required('Book')


class Review(db.Entity):
    text = orm.Required(str)
    book = orm.Required('Book')


class Author(db.Entity):
    name = orm.Required(str)
    books = orm.Set('Book')
    slug = orm.Optional(str, unique=True)

    def before_insert(self):
        self.slug = slugify(self.name)

    @property
    def url(self):
        return url_for('author', slug=self.slug)

    def __str__(self):
        return self.name


def populate_fields(book):
    data = fetch_json(book.isbn)
    try:
        # Extract the Volume Information
        volume_info = data['items'][0]['volumeInfo']
    except (KeyError, IndexError):
        print('Volume info not found')
    else:
        book.title = volume_info.get('title', '')
        book.subtitle = volume_info.get('subtitle', '')
        authors = volume_info.get('authors', [])
        for author in authors:
            db_row = Author.get(name=author)
            if not db_row:
                db_row = Author(name=author)
            book.authors.add(db_row)

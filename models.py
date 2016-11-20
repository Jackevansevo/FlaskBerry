from datetime import date
from flask import url_for
from pony import orm
from slugify import slugify

from scrape_info import fetch_json


# Establish Databse connection
db = orm.Database()


def add_book_copy(isbn):
    print(isbn)
    book = Book.get(isbn=isbn)
    if not book:
        # Creates book if it doesn't already exist
        book = Book(isbn=isbn)
    BookCopy(book=book)


class Customer(db.Entity):
    forename = orm.Required(str)
    surname = orm.Required(str)
    slug = orm.Optional(str, unique=True)
    loans = orm.Set('Loan')

    def before_insert(self):
        self.slug = slugify(str(self))

    def __str__(self):
        return ', '.join([self.forename, self.surname])


class Book(db.Entity):
    isbn = orm.PrimaryKey(str)
    title = orm.Optional(str)
    subtitle = orm.Optional(str)
    img = orm.Optional(str)
    slug = orm.Optional(str)

    genres = orm.Set('Genre')
    authors = orm.Set('Author')
    reviews = orm.Set('Review')
    copies = orm.Set('BookCopy')

    @property
    def num_copies(self):
        return orm.count(self.copies)

    @property
    def author_names(self):
        return ", ".join(author.name for author in self.authors)

    def before_insert(self):
        if self.isbn:
            populate_fields(self)
        self.slug = slugify(self.title)

    @property
    def url(self):
        return url_for('book', slug=self.slug)

    def __str__(self):
        return self.title


class BookCopy(db.Entity):
    book = orm.Required('Book')
    loans = orm.Set('Loan')


class Loan(db.Entity):
    start_date = orm.Required(date)
    end_date = orm.Required(date)
    customer = orm.Required('Customer')
    book = orm.Required('BookCopy')


class Genre(db.Entity):
    name = orm.Required(str)
    books = orm.Set('Book')

    def __str__(self):
        return self.name


class Review(db.Entity):
    text = orm.Required(str)
    book = orm.Required('Book')


class Author(db.Entity):
    name = orm.Required(str)
    books = orm.Set('Book')
    slug = orm.Optional(str)

    def before_insert(self):
        self.slug = slugify(self.name)

    @property
    def url(self):
        return url_for('author', slug=self.slug)

    def __str__(self):
        return self.name


def populate_fields(book):
    try:
        # Extract the Volume Information
        volume_info = fetch_json(book.isbn)['items'][0]['volumeInfo']
    except (KeyError, IndexError):
        print('Volume info not found')
    else:
        book.title = volume_info.get('title', '')
        book.subtitle = volume_info.get('subtitle', '')

        for name in volume_info.get('authors'):
            author = Author.get(name=name)
            if not author:
                author = Author(name=name)
            book.authors.add(author)

        for category in volume_info.get('categories'):
            genre = Genre.get(name=category)
            if not genre:
                genre = Genre(name=category)
            book.genres.add(genre)

        image_links = volume_info.get('imageLinks')
        if image_links:
            book.img = image_links.get('thumbnail')

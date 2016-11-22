from datetime import date, datetime
from flask import url_for
from slugify import slugify

from pony.orm import Optional, PrimaryKey, Required, Set, count, commit

from flaskberry import db
from flaskberry.isbn import meta


class Customer(db.Entity):
    forename = Required(str)
    surname = Required(str)
    email = Required(str)
    password = Required(str)
    slug = Optional(str, unique=True)
    loans = Set('Loan')

    def before_insert(self):
        self.slug = slugify(str(self))

    def __repr__(self):
        return '<Customer: {}>'.format(self.forename)

    def __str__(self):
        return ', '.join([self.forename, self.surname])


class Book(db.Entity):
    isbn = PrimaryKey(str)
    title = Optional(str)
    subtitle = Optional(str)
    img = Optional(str)
    slug = Optional(str)
    created_at = Required(datetime, sql_default='CURRENT_TIMESTAMP')

    genres = Set('Genre')
    authors = Set('Author')
    reviews = Set('Review')
    copies = Set('BookCopy')

    @property
    def num_copies(self):
        return count(self.copies)

    @property
    def author_names(self):
        return ", ".join(author.name for author in self.authors)

    def before_insert(self):
        meta_info = meta(self.isbn)
        self.title = meta_info.get('title')
        self.subtitle = meta_info.get('subtitle', '')
        self.img = meta_info.get('img')

        for category in meta_info.get('categories'):
            category = category.title()
            genre = Genre.get(name=category)
            if not genre:
                genre = Genre(name=category)
            self.genres.add(genre)

        for name in meta_info['authors']:
            author = get_or_create_author(name)
            self.authors.add(author)

        self.slug = slugify(self.title)

    @property
    def url(self):
        return url_for('book', slug=self.slug)

    def __repr__(self):
        return '<Book: {}>'.format(self.title)

    def __str__(self):
        return self.title


class BookCopy(db.Entity):
    book = Required('Book')
    loans = Set('Loan')

    def __repr__(self):
        return '<BookCopy: {}>'.format(self.book.ibsn)


class Loan(db.Entity):
    start_date = Required(date)
    end_date = Required(date)
    customer = Required('Customer')
    book = Required('BookCopy')

    def __repr__(self):
        return '<Loan: {}>'.format(self.start_date)


class Genre(db.Entity):
    name = Required(str, unique=True)
    books = Set('Book')
    slug = Optional(str)

    def before_insert(self):
        self.slug = slugify(self.name)

    @property
    def url(self):
        return url_for('genre', slug=self.slug)

    def __repr__(self):
        return '<Genre: {}>'.format(self.name)

    def __str__(self):
        return self.name


class Review(db.Entity):
    text = Required(str)
    book = Required('Book')

    def __str__(self):
        return self.text

    def __repr__(self):
        return '<Review: {}>'.format(self.book)


class Author(db.Entity):
    name = Required(str)
    books = Set('Book')
    slug = Optional(str)

    def before_insert(self):
        self.slug = slugify(self.name)

    @property
    def url(self):
        return url_for('author', slug=self.slug)

    def __repr__(self):
        return '<Author: {}>'.format(self.name)

    def __str__(self):
        return self.name


# [TODO] Move get_or_create functions into model definitions
def get_or_create_author(name):
    author = Author.get(name=name)
    if not author:
        author = Author(name=name)
        commit()
    return author


def get_or_create_book(isbn):
    book = Book.get(isbn=isbn)
    if not book:
        book = Book(isbn=isbn)
        commit()
    return book


def add_book_copy(isbn):
    book = get_or_create_book(isbn)
    if book:
        BookCopy(book=book)
        return book

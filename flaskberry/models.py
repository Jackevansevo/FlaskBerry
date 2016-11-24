from datetime import date, datetime, timedelta
from flask import url_for
from slugify import slugify
from flask_login import UserMixin
from titlecase import titlecase

from pony.orm import Optional, PrimaryKey, Required, Set, count, commit, select

from flaskberry import db, bcrypt
from flaskberry.isbn import meta


class Customer(db.Entity, UserMixin):
    forename = Required(str)
    surname = Required(str)
    email = Required(str)
    password = Required(bytes)
    slug = Optional(str, unique=True)
    loans = Set('Loan')
    book_allowance = Required(int, default=3)

    @property
    def is_admin(self):
        return False

    def get_id(self):
        return str(self.id)

    @property
    def read_list(self):
        """Returns set of all books a user has previously loaned"""
        return select(
            b for b in Book if self in b.copies.loans.customer
        ).distinct()

    def has_loaned(self, isbn):
        """Returns True if a user has previously loaned a book"""
        return select(
            l for l in Loan if l.book_copy.book.isbn == isbn).exists()

    def check_password(self, password):
        return bcrypt.check_password_hash(self.password, password)

    def has_book(self, isbn):
        return self.unreturned_loans.filter(
            lambda l: l.book_copy.book.isbn == isbn).exists()

    @property
    def unreturned_loans(self):
        return self.loans.select(lambda l: not l.returned)

    @property
    def can_loan(self):
        return len(self.unreturned_loans) < self.book_allowance

    @property
    def url(self):
        return url_for('customer', slug=self.slug)

    def before_insert(self):
        self.password = bcrypt.generate_password_hash(self.password)
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
    def is_available(self):
        """Returns True if any copies aren't currently on loan"""
        return not all([c.on_loan for c in self.copies])

    def get_available_copies(self):
        return [c for c in self.copies if not c.on_loan]

    def get_available_copy(self):
        return self.get_available_copies()[0]

    @property
    def num_available_copies(self):
        return len([c for c in self.copies if not c.on_loan])

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

        for category in meta_info.get('categories', []):
            category = titlecase(category)
            genre = Genre.get(name=category)
            if not genre:
                genre = Genre(name=category)
            self.genres.add(genre)

        for name in meta_info.get('authors'):
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

    @property
    def on_loan(self):
        """Returns True if a book copy has any outstanding loans"""
        return self.loans.select(lambda l: not l.returned).exists()

    def __repr__(self):
        return '<BookCopy: {}>'.format(self.book)


class Loan(db.Entity):
    start_date = Optional(date, sql_default='CURRENT_DATE')
    end_date = Optional(date)
    returned = Optional(bool, default=False)
    customer = Required('Customer')
    book_copy = Required('BookCopy')

    @property
    def due_in(self):
        return str((self.end_date - date.today()).days) + " Days"

    def after_insert(self):
        self.end_date = self.start_date + timedelta(days=7)

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
    rating = Required(int)
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

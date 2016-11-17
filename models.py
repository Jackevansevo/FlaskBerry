from pony import orm
from flask import url_for


from slugify import UniqueSlugify
from scrape_info import populate_fields


# Establish Databse connection
db = orm.Database()

# Create UniqueSlugify instance to generate slugs
slugify = UniqueSlugify(to_lower=True)


class Customer(db.Entity):
    forename = orm.Required(str)
    surname = orm.Required(str)
    books = orm.Set('Book')
    slug = orm.Optional(str, unique=True)

    def before_insert(self):
        self.slug = slugify(str(self))

    def __str__(self):
        return ', '.join([self.forename, self.surname])


class Authors(db.Entity):
    name = orm.Required(str)

    def __str__(self):
        return self.name


class Book(db.Entity):
    title = orm.Optional(str)
    subtitle = orm.Optional(str)
    author = orm.Optional(str)
    genre = orm.Optional(str)
    isbn = orm.Optional(str, unique=True)
    img = orm.Optional(str)
    lender = orm.Optional(Customer)
    slug = orm.Optional(str, unique=True)

    def before_insert(self):
        if self.isbn:
            populate_fields(self)
        self.slug = slugify(self.title)

    def url(self):
        return url_for('book', slug=self.slug)

    def __str__(self):
        return self.title

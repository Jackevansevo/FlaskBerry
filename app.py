from flask import Flask, render_template, redirect, url_for

from forms import BookSubmissionForm
from models import db, Book, Customer, Author
from pony import orm


# create our little application :)
app = Flask(__name__)
app.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RT'

app.config.update(
    RECAPTCHA_PUBLIC_KEY='6LeETwwUAAAAAL5rVTXPPL43LlTvf9UxkZaMQkx9',
    RECAPTCHA_PRIVATE_KEY='6LeETwwUAAAAAHeM3iF8WZsj0T8tJN_62JsB9XBq'
)

db.bind('sqlite', 'db.sqlite', create_db=True)
db.generate_mapping(create_tables=True)
orm.sql_debug(True)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/books')
@orm.db_session(strict=True)
def books():
    books = Book.select()
    return render_template('books.html', books=books)


@app.route('/books/<slug>')
@orm.db_session(strict=True)
def book(slug):
    book = Book.get(slug=slug)
    return render_template('book_page.html', book=book)


@app.route('/authors')
@orm.db_session(strict=True)
def authors():
    authors = Author.select().distinct()
    return render_template('authors.html', authors=authors)


@app.route('/authors/<slug>')
@orm.db_session(strict=True)
def author(slug):
    author = Author.get(slug=slug)
    return render_template('author_page.html', author=author)


@app.route('/customers')
@orm.db_session(strict=True)
def customers():
    customers = Customer.select()
    return render_template('customers.html', customers=customers)


@app.route('/add-book', methods=['POST', 'GET'])
@orm.db_session(strict=True)
def add_book():
    """Simple view to add a book"""
    form = BookSubmissionForm()
    if form.validate_on_submit():
        Book(isbn=form.isbn.data)
        orm.commit()
        return redirect(url_for('books'))
    return render_template('add_book.html', form=form)


if __name__ == '__main__':
    app.run(debug=True)

from flask import Flask, render_template, flash, redirect, url_for

from forms import BookSubmissionForm
from models import db, Book, Customer
from pony import orm


# create our little application :)
app = Flask(__name__)
app.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RT'


db.bind('sqlite', 'db.sqlite', create_db=True)
db.generate_mapping(create_tables=True)
orm.sql_debug(True)


@app.route('/')
@orm.db_session(strict=True)
def index():
    books = Book.select()
    return render_template('index.html', books=books)


@app.route('/customers')
@orm.db_session(strict=True)
def customers():
    customers = Customer.select()
    return render_template('customers.html', customers=customers)


@app.route('/add-book', methods=['POST', 'GET'])
def add_book():
    """Simple view to add a book"""
    form = BookSubmissionForm()
    if form.validate_on_submit():
        try:
            with orm.db_session:
                Book(isbn=form.isbn.data)
                orm.commit()
        except orm.core.TransactionIntegrityError:
            flash('Book already exists!')
        else:
            return redirect(url_for('index'))
    return render_template('add_book.html', form=form)


@app.route('/book/<slug>')
def book(slug):
    with orm.db_session:
        book = Book.get(slug=slug)
    return render_template('book_page.html', book=book)


if __name__ == '__main__':
    app.run(debug=True)

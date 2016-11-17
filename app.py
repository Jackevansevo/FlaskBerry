from flask import Flask, render_template, request, flash, redirect, url_for
import os

from models import db, Book
from pony import orm


# create our little application :)
app = Flask(__name__)
app.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RT'


db.bind('sqlite', 'db.sqlite', create_db=True)
db.generate_mapping(create_tables=True)
orm.sql_debug(True)


# Load default config and override config from an environment variable
app.config.update(dict(
    DATABASE=os.path.join(app.root_path, 'db.sqlite'),
    SECRET_KEY='\xcb-\xb0\xa3$\xf0t\x88\xd4a\x19Q_\x0f-\xd0F\xe2\x0c\xd4Mf',
    USERNAME='admin',
    PASSWORD='default'
))
app.config.from_envvar('FLASKR_SETTINGS', silent=True)


@app.route('/')
def index():
    with orm.db_session:
        books = Book.select()[:]
    return render_template('index.html', books=books)


@app.route('/add-book', methods=['POST', 'GET'])
def add_book():
    """Simple view to add a book"""
    if request.method == 'POST':
        form = request.form
        try:
            with orm.db_session:
                Book(isbn=form['isbn'])
                orm.commit()
        except orm.core.TransactionIntegrityError:
            flash('Book already exists!')
        else:
            return redirect(url_for('index'))
    return render_template('add_book.html')


@app.route('/book/<slug>')
def book(slug):
    with orm.db_session:
        book = Book.get(slug=slug)
    return render_template('book_page.html', book=book)


def valid_isbn(isbn):
    listofnums = [int(digit) for digit in isbn]
    multipliers = reversed(range(2, 12))
    multipliednums = [a*b for a, b in zip(listofnums, multipliers)]
    return sum(multipliednums) % 11

if __name__ == '__main__':
    app.run(debug=True)

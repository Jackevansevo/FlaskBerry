from flask import Flask, flash, redirect, render_template, request, url_for

from forms import BookSubmissionForm
from models import db, Book, Customer, Author, add_book_copy
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


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/books', methods=['POST', 'GET'])
@orm.db_session
def books():
    if request.method == 'POST':
        query = request.form['query']
        books = orm.select(b for b in Book if query in b.title)
        return render_template('books.html', books=books)
    books = Book.select()
    return render_template('books.html', books=books)


@app.route('/books/<slug>')
@orm.db_session
def book(slug):
    book = Book.get(slug=slug)
    return render_template('book_page.html', book=book)


@app.route('/authors')
@orm.db_session
def authors():
    authors = Author.select()
    return render_template('authors.html', authors=authors)


@app.route('/authors/<slug>')
@orm.db_session
def author(slug):
    author = Author.get(slug=slug)
    return render_template('author_page.html', author=author)


@app.route('/customers')
@orm.db_session
def customers():
    customers = Customer.select()
    return render_template('customers.html', customers=customers)


@app.route('/add-book', methods=['POST', 'GET'])
@orm.db_session
def add_book():
    """Simple view to add a book"""
    form = BookSubmissionForm()
    if form.validate_on_submit():
        add_book_copy(form.isbn.data)
        return redirect(url_for('books'))
    return render_template('add_book.html', form=form)


@app.route('/delete-book/<isbn>', methods=['POST'])
@orm.db_session
def delete_book(isbn):
    book = Book.get(isbn=isbn)
    book.delete()
    flash('Book deleted: {}'.format(book))
    return redirect(url_for('books'))


if __name__ == '__main__':
    app.run(debug=True)

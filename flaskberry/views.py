from flask import abort, flash, redirect, render_template, request, url_for

from flask_login import (
    current_user, login_user, logout_user, login_required, LoginManager
)

from urllib.parse import urlparse, urljoin

from pony.orm import select, desc, commit

from flaskberry import app

from .forms import BookSubmissionForm, LoginForm
from .models import Author, Book, Customer, Genre, Loan, add_book_copy

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.session_protection = "strong"
login_manager.login_view = "login"

# [TODO] Random book of the day
# [TODO] Reminder email when book is due


def is_safe_url(target):
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ('http', 'https') and \
        ref_url.netloc == test_url.netloc


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/books', methods=['GET', 'POST'])
def books():
    if request.method == 'POST':
        return redirect(url_for('search_books', query=request.form['query']))
    books = Book.select().order_by(desc(Book.created_at))
    return render_template('books.html', books=books)


@app.route('/books/search/<string:query>')
def search_books(query):
    books = select(b for b in Book if query in b.title)
    books = books.order_by(desc(Book.created_at))
    return render_template('books.html', books=books)


@app.route('/books/<string:slug>')
def book(slug):
    book = Book.get(slug=slug)
    if not book:
        abort(404, "Book '{}'  not found".format(slug))
    return render_template('book_page.html', book=book)


@app.route('/books/random')
def random_book():
    book = Book.select_random(1)[0]
    return render_template('book_page.html', book=book)


@app.route('/authors', methods=['GET', 'POST'])
def authors():
    if request.method == 'POST':
        return redirect(url_for('search_authors', query=request.form['query']))
    authors = Author.select().order_by(Author.name)
    return render_template('authors.html', authors=authors)


@app.route('/authors/search/<string:query>')
def search_authors(query):
    authors = select(a for a in Author if query in a.name)
    return render_template('authors.html', authors=authors)


@app.route('/authors/<slug>')
def author(slug):
    author = Author.get(slug=slug)
    if not author:
        abort(404, "Author: '{}' not found".format(slug))
    return render_template('author_page.html', author=author)


@app.route('/genres', methods=['GET', 'POST'])
def genres():
    if request.method == 'POST':
        return redirect(url_for('search_genres', query=request.form['query']))
    genres = Genre.select().order_by(Genre.name)
    return render_template('genres.html', genres=genres)


@app.route('/genres/search/<string:query>')
def search_genres(query):
    genres = select(g for g in Genre if query in g.name)
    return render_template('genres.html', genres=genres)


@app.route('/genres/<slug>')
def genre(slug):
    genre = Genre.get(slug=slug)
    if not genre:
        abort(404, "Genre: '{}' not found".format(slug))
    return render_template('genre_page.html', genre=genre)


@app.route('/customer/<string:slug>')
@login_required
def customer(slug):
    customer = Customer.get(slug=slug)
    if not customer:
        abort(404, "Customer: '{}' not found".format(slug))
    return render_template('customer_page.html', customer=customer)


@app.route('/customers')
def customers():
    customers = Customer.select()
    return render_template('customers.html', customers=customers)


@app.route('/add-book', methods=['GET', 'POST'])
def add_book():
    """Simple view to add a book"""
    form = BookSubmissionForm()
    if form.validate_on_submit():
        book = add_book_copy(form.isbn.data)
        return redirect(url_for('book', slug=book.slug))
    return render_template('add_book.html', form=form)


@app.errorhandler(404)
def page_not_found(error):
    return render_template('404.html', error=error), 404


@app.route('/delete-book/<isbn>', methods=['POST'])
def delete_book(isbn):
    book = Book.get(isbn=isbn)
    book.delete()
    flash('Book deleted: {}'.format(book))
    return redirect(url_for('books'))


@app.route('/checkout-book/<slug>', methods=['POST'])
@login_required
def checkout_book(slug):
    customer = Customer.get(email=current_user.email)
    book = Book.get(slug=slug)
    if customer.can_loan and book.is_available:
        book_copy = book.get_available_copy()
        Loan(customer=customer, book_copy=book_copy)
        commit()
    return redirect(url_for('book', slug=slug))


@login_manager.user_loader
def load_user(user_id):
    return Customer.get(id=user_id)


@app.route('/return-book/<slug>', methods=['POST'])
@login_required
def return_book(slug):
    customer = Customer.get(email=current_user.email)
    # Find the customers corresponding outstanding loans which match the slug
    loan = customer.loans.select(
        lambda l: not l.returned and l.book_copy.book.slug == slug).first()
    loan.returned = True
    commit()
    return redirect(url_for('book', slug=slug))


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = Customer.get(email=form.email.data)
        login_user(user)
        flash('Logged in successfully')
        next = request.args.get('next')
        if not is_safe_url(next):
            return abort(400)
        return redirect(next or url_for('index'))
    return render_template('login.html', form=form)


@app.route('/logout', methods=['POST'])
@login_required
def logout():
    logout_user()
    flash('Logged out')
    next = request.args.get('next')
    if not is_safe_url(next):
        return abort(400)
    return redirect(next or url_for('index'))

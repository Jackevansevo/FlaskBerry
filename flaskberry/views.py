from flask import abort, flash, redirect, render_template, request, url_for

from urllib.parse import urlparse, urljoin

from pony.orm import select, desc

from flaskberry import app

from .forms import BookSubmissionForm, BookCheckoutForm
from .models import Book, Customer, Author, Genre, add_book_copy


def is_safe_url(target):
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ('http', 'https') and \
        ref_url.netloc == test_url.netloc


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/books', methods=['POST', 'GET'])
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


@app.route('/authors', methods=['POST', 'GET'])
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


@app.route('/genres', methods=['POST', 'GET'])
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


@app.route('/customers')
def customers():
    customers = Customer.select()
    return render_template('customers.html', customers=customers)


@app.route('/add-book', methods=['POST', 'GET'])
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


@app.route('/checkout-book/<slug>', methods=['POST', 'GET'])
def checkout_book(slug):
    book = Book.get(slug=slug)
    form = BookCheckoutForm()
    if form.validate_on_submit():
        assert False
    else:
        print(form.errors)
    form = BookCheckoutForm(isbn=book.isbn)
    return render_template('checkout.html', form=form)


if __name__ == '__main__':
    app.run(debug=True)

from flask import flash, redirect, render_template, request, url_for

from urllib.parse import urlparse, urljoin

from pony.orm import select, desc

from flaskberry import app

from .forms import BookSubmissionForm
from .models import Book, Customer, Author, add_book_copy, Genre


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
        query = request.form['query']
        books = select(b for b in Book if query in b.title)
        if not books.exists():
            flash('No results found')
        return render_template('books.html', books=books)
    books = Book.select().order_by(desc(Book.created_at))
    return render_template('books.html', books=books)


@app.route('/books/<slug>')
def book(slug):
    book = Book.get(slug=slug)
    return render_template('book_page.html', book=book)


@app.route('/genres', methods=['POST', 'GET'])
def genres():
    if request.method == 'POST':
        query = request.form['query']
        genres = select(g for g in Genre if query in g.name)
        if not genres.exists():
            flash('No results found')
        return render_template('genres.html', genres=genres)
    genres = Genre.select()
    return render_template('genres.html', genres=genres)


@app.route('/genres/<slug>')
def genre(slug):
    genre = Genre.get(slug=slug)
    return render_template('genre_page.html', genre=genre)


@app.route('/authors', methods=['POST', 'GET'])
def authors():
    if request.method == 'POST':
        query = request.form['query']
        authors = select(a for a in Author if query in a.name)
        if not authors.exists():
            flash('No results found')
        return render_template('authors.html', authors=authors)
    authors = Author.select().order_by(Author.name)
    return render_template('authors.html', authors=authors)


@app.route('/authors/<slug>')
def author(slug):
    author = Author.get(slug=slug)
    return render_template('author_page.html', author=author)


@app.route('/customers')
def customers():
    customers = Customer.select()
    return render_template('customers.html', customers=customers)


@app.route('/add-book', methods=['POST', 'GET'])
def add_book():
    """Simple view to add a book"""
    form = BookSubmissionForm()
    if form.validate_on_submit():
        add_book_copy(form.isbn.data)
        return redirect(url_for('books'))
    return render_template('add_book.html', form=form)


@app.route('/delete-book/<isbn>', methods=['POST'])
def delete_book(isbn):
    book = Book.get(isbn=isbn)
    book.delete()
    flash('Book deleted: {}'.format(book))
    return redirect(url_for('books'))


if __name__ == '__main__':
    app.run(debug=True)

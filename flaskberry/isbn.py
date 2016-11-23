"""
All ISBN Logic sourced from:
https://en.wikipedia.org/wiki/International_Standard_Book_Number
"""

from itertools import islice, cycle
from re import sub, compile
from requests import get
from requests.exceptions import RequestException
from os import environ

# [TODO] Scrape meta data from multiple sources


googb_api_url = 'https://www.googleapis.com/books/v1/volumes?q=isbn:{}&key={}'
api_key = environ['BOOKS_API_KEY']

wcat_api_url = 'http://xisbn.worldcat.org/webservices/xid/isbn/{}'\
    + '?method=getMetadata&fl=*&format=json'


CLEAN_REGEX_PATTERN = compile('[^\dX]')


class InvalidISBNError(Exception):
    pass


class MetaDataNotFoundError(Exception):
    pass


def _calc_isbn_13_check_digit(isbn):
    multipliers = islice(cycle([1, 3]), 12)
    res = 10 - sum([int(a)*b for a, b in zip(isbn, multipliers)]) % 10
    return 0 if res == 10 else res


def to_isbn13(isbn):
    if len(isbn) == 13:
        return isbn
    isbn = '978' + isbn
    return isbn[:-1] + str(_calc_isbn_13_check_digit(isbn))


def is_isbn13(isbn):
    return not sum([int(a)*b for a, b in zip(isbn, cycle([1, 3]))]) % 10


def _calc_isbn_10_check_digit(isbn):
    res = 11 - sum([int(a)*b for a, b in zip(isbn, range(10, 1, -1))]) % 11
    return 'X' if res == 10 else res


def to_isbn10(isbn):
    if len(isbn) == 10:
        return isbn
    isbn = isbn[3:]
    return isbn[:-1] + str(_calc_isbn_10_check_digit(isbn))


def is_isbn10(isbn):
    isbn_num = [10 if digit == 'X' else int(digit) for digit in isbn]
    return not sum([a*b for a, b in zip(isbn_num, range(10, 0, -1))]) % 11


def isbn_is_valid(isbn):
    if len(isbn) == 10:
        return is_isbn10(isbn)
    elif len(isbn) == 13:
        return is_isbn13(isbn)
    return False


def clean(isbn):
    return sub(CLEAN_REGEX_PATTERN, '', isbn)


def request_data(isbn, url, key=None):
    try:
        r = get(url.format(isbn, key)).json()
    except(ValueError, RequestException):
        pass
    else:
        return r


def _scrape_goob(isbn):
    META_KEYS = ('title', 'subtitle', 'authors', 'categories')
    res = request_data(isbn, googb_api_url, key=api_key)
    if res.get('totalItems', 0) == 0:
        raise MetaDataNotFoundError('Unable to find', isbn)
    info = next(iter(res['items']))['volumeInfo']
    meta = {k: v for k, v in info.items() if k in META_KEYS}
    meta['img'] = info['imageLinks']['thumbnail']
    return meta


def _scrape_wcat(isbn):
    META_KEYS = ('title', 'author')
    res = request_data(isbn, wcat_api_url)
    return res
    # info = next(iter(res['items']))['volumeInfo']
    # meta = {k: v for k, v in info.items() if k in META_KEYS}
    # meta['img'] = info['imageLinks']['thumbnail']
    # return meta


def meta(isbn):
    if not isbn_is_valid(isbn):
        raise InvalidISBNError('Invalid ISBN', isbn)
    data = _scrape_goob(isbn)
    if not data:
        data = _scrape_wcat(isbn)
    return data

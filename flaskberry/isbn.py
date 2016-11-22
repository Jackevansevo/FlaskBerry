"""
All ISBN Logic sourced from:
https://en.wikipedia.org/wiki/International_Standard_Book_Number
"""

from itertools import islice, cycle
from re import sub, compile
from requests import get
from requests.exceptions import RequestException
from os import environ

api_url = 'https://www.googleapis.com/books/v1/volumes?q=isbn:{}&key={}'
api_key = environ['BOOKS_API_KEY']
META_KEYS = ('title', 'subtitle', 'authors', 'categories')

CLEAN_REGEX_PATTERN = compile('[^\dX]')


class InvalidISBNError(Exception):
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


def meta(isbn):
    if not isbn_is_valid(isbn):
        raise InvalidISBNError('Invalid ISBN', isbn)
    try:
        r = get(api_url.format(isbn, api_key)).json()
    except (ValueError, RequestException):
        pass
    else:
        info = next(iter(r['items']))['volumeInfo']
        meta = {k: v for k, v in info.items() if k in META_KEYS}
        meta['img'] = info['imageLinks']['thumbnail']
        return meta


def isbn_is_valid(isbn):
    if len(isbn) == 10:
        return is_isbn10(isbn)
    elif len(isbn) == 13:
        return is_isbn13(isbn)
    return False


def clean(isbn):
    return sub(CLEAN_REGEX_PATTERN, '', isbn)

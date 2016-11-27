"""
All ISBN Logic sourced from:
https://en.wikipedia.org/wiki/International_Standard_Book_Number
"""

from itertools import islice, cycle
from re import sub, compile
from requests import get
from requests.exceptions import RequestException
from os import environ


api_key = environ['BOOKS_API_KEY']

googb_api_url = 'https://www.googleapis.com/books/v1/volumes?q=isbn:{}&key={}'

wcat_api_url = (
    'http://xisbn.worldcat.org/webservices/xid/isbn/{}'
    '?method=getMetadata&fl=*&format=json'
)

open_library_api = (
    'http://openlibrary.org/api/books?bibkeys=ISBN:{}'
    '&jscmd=data&format=json'
)


meta_cache = {}

CLEAN_REGEX_PATTERN = compile('[^\dX]')
AUTHOR_SUB_REGEX = compile('[^a-zA-Z\s+]|\s\;')


# [TODO] Write function that looks up region of isbn


class InvalidISBNError(Exception):
    pass


class MetaDataNotFoundError(Exception):
    pass


def has_english_identifier(isbn):
    # https://en.wikipedia.org/wiki/List_of_ISBN_identifier_groups
    identifier_group = ('0', '1')
    if len(isbn) == 10:
        # e.g. 0198739834
        if isbn[0] in identifier_group:
            return True
    elif len(isbn) == 13:
        # e.g. 9780198739838
        if isbn[:3] == '978' and isbn[3] in identifier_group:
            return True
    return False


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
    sum_products = sum([int(a)*b for a, b in zip(isbn, range(10, 1, -1))])
    rem = (11 - sum_products % 11) % 11
    return 'X' if rem == 10 else rem


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
        r = get(url.format(isbn, key))
    except RequestException:
        pass
    else:
        return r


def request_json(isbn, url, key=None):
    try:
        json = request_data(isbn, url, key).json()
    except(ValueError):
        pass
    return json


def get_amazon_image(isbn):
    """Tries to return image url from Amazon, returns placeholder fallback"""
    # Amazon only provides book images for isbn10's
    image_url = 'http://images.amazon.com/images/P/{}'.format(to_isbn10(isbn))
    try:
        r = get(image_url)
    except RequestException:
        return
    else:
        if r.headers['Content-Type'] != 'image/gif':
            return image_url
        else:
            return 'http://placehold.it/150x225'


# Caution here be dragons, enter at your own peril
scrape_strategies = []


def scrape_stategy(scrape_func):
    """Adds all functions with a scrape_stategy to a list"""
    scrape_strategies.append(scrape_func)
    return scrape_func


@scrape_stategy
def _scrape_goob(isbn):
    META_KEYS = ('title', 'subtitle', 'authors', 'categories')
    res = request_json(isbn, googb_api_url, key=api_key)
    if res.get('totalItems', 0) != 0:
        info = next(iter(res['items']))['volumeInfo']
        meta = {k: v for k, v in info.items() if k in META_KEYS}
        if meta:
            try:
                meta['img'] = info['imageLinks']['thumbnail']
            except KeyError:
                return
        return meta


@scrape_stategy
def _scrape_openlibrary(isbn):
    res = request_json(isbn, open_library_api)
    if res:
        info = next(iter(res.values()))
        META_KEYS = ('title', 'subtitle', 'authors', 'subjects')
        meta = {k: v for k, v in info.items() if k in META_KEYS}
        if 'authors' not in meta:
            return
        meta['authors'] = [author['name'] for author in meta['authors']]
        meta['categories'] = [sub['name'] for sub in meta.pop('subjects')]
        cover = info.get('cover', {})
        meta['img'] = cover.get('image') or get_amazon_image(isbn)
        return meta


@scrape_stategy
def _scrape_wcat(isbn):
    META_KEYS = ('title', 'author')
    res = request_json(isbn, wcat_api_url)
    if res.get('stat') == 'ok':
        info = next(iter(res['list']))
        meta = {k: v for k, v in info.items() if k in META_KEYS}
        meta['img'] = get_amazon_image(isbn)
        if 'authors' not in meta:
            return
        meta['authors'] = [
            sub(AUTHOR_SUB_REGEX, '', e.strip())
            for e in meta.pop('author').split('and')
        ]
        return meta


def meta(isbn):
    if not isbn_is_valid(isbn):
        raise InvalidISBNError('Invalid ISBN', isbn)

    # Check the cache
    if isbn in meta_cache:
        return meta_cache[isbn]

    # Loops through each scrape_stategy and returns first non empty result
    for strat in scrape_strategies:
        data = strat(isbn)
        if data:
            print(strat.__name__)
            # Save the result in cache
            meta_cache[isbn] = data
            return data

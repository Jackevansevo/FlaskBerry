import requests

google_books_api = 'https://www.googleapis.com/books/v1/volumes?q=isbn:'


# Boolean flag determining whether user data is clobbered
overrite_metadata = True


def fetch_json(isbn):
    try:
        r = requests.get(google_books_api + isbn)
    except requests.exceptions.RequestException:
        print('ISBN: {} not found'.format(isbn))
        return
    else:
        try:
            data = r.json()
        except ValueError:
            print('JSON decoding failed fetching: {}'.format(isbn))
        else:
            # Don't bother returning anything if there are no items in JSON
            if data.get('totalItems', 0) == 0:
                return
            return data

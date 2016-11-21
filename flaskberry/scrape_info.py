import requests
import os

api_url = 'https://www.googleapis.com/books/v1/volumes?q=isbn:{}&key={}'


def fetch_json(isbn):
    try:
        api_key = os.environ['BOOKS_API_KEY']
    except KeyError:
        print('Google Books API Key not found aborting')
        return {}
    else:
        try:
            r = requests.get(api_url.format(isbn, api_key))
        except requests.exceptions.RequestException:
            print('ISBN: {} not found'.format(isbn))
            return {}
        else:
            try:
                data = r.json()
            except ValueError:
                print('JSON decoding failed fetching: {}'.format(isbn))
            else:
                return data

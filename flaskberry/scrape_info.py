import requests
import os

api_url = 'https://www.googleapis.com/books/v1/volumes?q=isbn:{}&key={}'


def fetch_json(isbn):
    try:
        api_key = os.environ['BOOKS_API_KEY']
    except KeyError:
        print('Google Books API Key not found aborting')
        raise Exception('ISBN: {} not found'.format(isbn))
    else:
        try:
            r = requests.get(api_url.format(isbn, api_key))
        except requests.exceptions.RequestException:
            raise Exception('ISBN: {} not found'.format(isbn))
        else:
            try:
                data = r.json()
            except ValueError:
                raise Exception('JSON decoding failed')
            else:
                try:
                    volume_info = data['items'][0]['volumeInfo']
                except(KeyError, IndexError):
                    print('Volume info not found')
                    raise Exception('Volume info not found')
                else:
                    return volume_info

import requests

# [TODO] Should be able to populate a books data given just a isbn or book
# title (prefer ISBN's, fallback to title)

# [TODO] Register a google Books API key to prevent being rate limited
google_books_api = 'https://www.googleapis.com/books/v1/volumes?q=isbn:'
amazon_images_api = 'http://images.amazon.com/images/P/'


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


def populate_fields(book):
    data = fetch_json(book.isbn)
    if data:
        try:
            # Extract the Volume Information
            volume_info = data['items'][0]['volumeInfo']
        except (KeyError, IndexError):
            print('Volume info not found')
            pass
        else:
            try:
                book.title = volume_info['title']
            except KeyError:
                pass
            try:
                book.subtitle = volume_info['subtitle']
            except KeyError:
                pass
            try:
                book.img = volume_info['imageLinks']['thumbnail']
            except KeyError:
                pass
            try:
                book.author = ' '.join(volume_info['authors'])
            except KeyError:
                pass

    if not book.img:
        book.img = amazon_images_api + book.isbn


if __name__ == '__main__':
    print(fetch_json('0593060504'))

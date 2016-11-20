from flask_wtf import FlaskForm
from wtforms import StringField, ValidationError
from wtforms.validators import DataRequired
from itertools import islice, cycle

import re


def calc_isbn_13_check_digit(isbn):
    # wikipedia.org/wiki/International_Standard_Book_Number#ISBN-13_check_digit_calculation
    multipliers = islice(cycle([1, 3]), 12)
    res = 10 - sum([a*b for a, b in zip(isbn, multipliers)]) % 10
    return 0 if res == 10 else res


def convert_isbn10_to_isbn13(isbn):
    # wikipedia.org/wiki/International_Standard_Book_Number#ISBN-10_to_ISBN-13_conversion
    isbn = [9, 7, 8] + isbn
    isbn[-1] = calc_isbn_13_check_digit(isbn)
    return isbn


def isbn_13_is_valid(isbn):
    return not sum([a*b for a, b in zip(isbn, cycle([1, 3]))]) % 10


class BookSubmissionForm(FlaskForm):
    isbn = StringField(
        'Book ISBN number e.g. 0545582970 (Harry Potter)',
        validators=[DataRequired()]
    )

    def validate_isbn(form, field):

        # Replace whitespace and dashes
        field.data = re.sub(r'[\s+-]', '', field.data)

        try:
            isbn = [int(digit) for digit in field.data]
        except ValueError:
            raise ValidationError('Invalid characters in ISBN')

        if len(isbn) == 10:
            # Converts isbn10 to isbn13
            isbn = convert_isbn10_to_isbn13(isbn)

        if not isbn_13_is_valid(isbn):
            raise ValidationError('ISBN Number was Invalid')

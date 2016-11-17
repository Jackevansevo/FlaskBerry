from flask_wtf import FlaskForm
from wtforms import StringField, ValidationError
from wtforms.validators import DataRequired

import re


class BookSubmissionForm(FlaskForm):
    isbn = StringField(
        'ISBN e.g. 0545582970 (Harry Potter)',
        validators=[DataRequired()]
    )

    def validate_isbn(form, field):
        # Replace whitespace and dashes
        field.data = re.sub(r'[\s+-]', '', field.data)
        # wikipedia.org/wiki/International_Standard_Book_Number#Check_digits
        nums = [int(digit) for digit in field.data]
        rem = sum([a*b for a, b in zip(nums, range(10, 0, -1))]) % 11
        if bool(rem % 11):
            raise ValidationError('Invalid ISBN Number')

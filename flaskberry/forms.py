from flask_wtf import FlaskForm
from wtforms import StringField, ValidationError
from wtforms.validators import DataRequired
from flaskberry.isbn import canonical, to_isbn13, is_isbn13


class BookSubmissionForm(FlaskForm):
    isbn = StringField(
        'Book ISBN number e.g. 0545582970 (Harry Potter)',
        validators=[DataRequired()]
    )

    def validate_isbn(form, field):
        field.data = canonical(field.data)
        field.data = to_isbn13(field.data)
        if not is_isbn13(field.data):
            raise ValidationError('ISBN Number was Invalid')

from flask_wtf import FlaskForm
from wtforms import IntegerField, StringField, ValidationError
from wtforms.validators import DataRequired
from flaskberry.isbn import clean, to_isbn13, is_isbn13, meta, InvalidISBNError
from flaskberry.models import Book, Customer


class BookSubmissionForm(FlaskForm):
    isbn = StringField(
        'Book ISBN number e.g. 0545582970 (Harry Potter)',
        validators=[DataRequired()]
    )

    def validate_isbn(form, field):
        field.data = clean(field.data)
        field.data = to_isbn13(field.data)
        if not is_isbn13(field.data):
            raise ValidationError('ISBN Number was Invalid')
        try:
            meta(field.data)
        except InvalidISBNError:
            raise ValidationError('Book metadata not found') from None


class BookCheckoutForm(FlaskForm):
    customer = IntegerField(validators=[DataRequired()])
    isbn = StringField(validators=[DataRequired()])

    def validate_isbn(form, field):
        if not Book.get(isbn=field.data):
            raise ValidationError('Book not found')

    def validate_customer(form, field):
        if not Customer.get(id=field.data):
            raise ValidationError('Customer not found')

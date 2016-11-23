from flask_wtf import FlaskForm
from wtforms import IntegerField, StringField, PasswordField, ValidationError
from wtforms.validators import DataRequired

from .isbn import clean, to_isbn13, is_isbn13, meta, InvalidISBNError
from .models import Book, Customer


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


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])

    def validate(self):
        rv = FlaskForm.validate(self)
        if not rv:
            return False
        user = Customer.get(email=self.email.data)
        if user is None:
            error_msg = 'Unable to find customer with matching email in system'
            self.email.errors.append(error_msg)
            return False

        if not user.check_password(self.password.data):
            self.password.errors.append('Password incorrect')
            return False

        self.user = user
        return True

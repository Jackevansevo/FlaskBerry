from flask_wtf import FlaskForm

from wtforms import IntegerField, PasswordField, StringField, ValidationError

from wtforms.validators import DataRequired, Email

from .isbn import clean, to_isbn13, is_isbn13, meta, has_english_identifier
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
        if not has_english_identifier(field.data):
            error_msg = 'ISBN Contains a non English-language identifier'
            raise ValidationError(error_msg)
        if not meta(field.data):
            raise ValidationError('Book Meta-data not found')


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
    email = StringField('Email', validators=[DataRequired(), Email()])
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
            self.password.errors.append('Invalid password')
            return False

        self.user = user
        return True


class AuthorForm(FlaskForm):
    name = StringField(validators=[DataRequired()])


class GenreUpdateForm(FlaskForm):
    name = StringField(validators=[DataRequired()])


class BookForm(FlaskForm):
    title = StringField(validators=[DataRequired()])
    subtitle = StringField()
    img = StringField('The image URL')

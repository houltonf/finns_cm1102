from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField, BooleanField
from wtforms.validators import DataRequired, ValidationError, Regexp, EqualTo
from shop.models import User


class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(message="Username is required"),
    Regexp('([A-z]|[0-9]){5,20}',message="Username must be between 5 and 20 characters, and only contain letters and/or numbers.")])
    password = PasswordField('Password', validators=[DataRequired(message="Password is required"),
    Regexp('([A-z]|[0-9]){5,20}',message="Password must be between 5 and 20 characters, and only contain letters and/or numbers."),
    EqualTo('confirm_password',message="Passwords don't match. Try again.")])
    confirm_password = PasswordField('Confirm password', validators=[DataRequired(message="Please confirm your password"),
    Regexp('([A-z]|[0-9]){5,20}',message="Password must be between 5 and 20 characters, and only contain letters and/or numbers.")])
    email = StringField('Email')
    submit = SubmitField('Register')

    def validate_username(self, username):
        user = User.query.filter_by(username = username.data).first()
        if user is not None:
            raise ValidationError('Username has been taken. Please choose another.')

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(message="Please enter a username"),
    Regexp('([A-z]|[0-9]){5,20}',message="Username must be between 5 and 20 characters, and only contain letters and/or numbers.")])
    password = PasswordField('Password', validators=[DataRequired(message="Please enter a password"),
    Regexp('([A-z]|[0-9]){5,20}',message="Password must be between 5 and 20 characters, and only contain letters and/or numbers.")])
    submit = SubmitField('Login')

class AddtoCart(FlaskForm):
    add = SubmitField('Add to Cart')
    details = SubmitField('Product details')
    remove = SubmitField('Remove from cart')
    checkout = SubmitField('CHECKOUT')

class ItemFilter(FlaskForm):
    sort_type=SelectField("Sort by",
    choices=[("default", "Filter..."), ("price_high", "High price"),("price_low", "Low price"), ("eco_low", "Low eco")],
    default="default",
    render_kw={"onchange": "this.form.submit()"})

class CheckoutForm(FlaskForm):
    name = StringField('Full name', validators=[DataRequired(message="Name is required"),         # https://wtforms.readthedocs.io/en/2.3.x/validators/
    Regexp('[A-z]', message="Name can only contain letters and spaces.")])
    card_no = StringField('Card number', validators=[DataRequired(message="Card number is required"),
    Regexp('[0-9]{16}', message="Card number must contain 16 numbers (no spaces).")])
    gift = BooleanField("This order contains a gift")               # "Basic Fields" : https://wtforms.readthedocs.io/en/2.3.x/fields/
    recommend = BooleanField("I would recommend Boujee Flatpacks")
    comments = StringField("(Optional) Any further comments you would like to leave for our staff?")
    submit = SubmitField("Shiny 'Place Order' button")

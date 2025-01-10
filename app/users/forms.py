from flask_wtf import FlaskForm
from wtforms.fields.simple import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Length, Email, EqualTo


class LoginForm(FlaskForm):
    username = StringField(
        'Username',
        validators=[DataRequired(), Length(min=3, max=50)],
        render_kw={"placeholder": "Enter your username"}
    )
    password = PasswordField(
        'Password',
        validators=[DataRequired(), Length(min=6, max=128)],
        render_kw={"placeholder": "Enter your password"}
    )
    login = SubmitField('Login')

class RegistrationForm(FlaskForm):
    username = StringField(
        'Username',
        validators=[DataRequired(), Length(min=3, max=50)],
        render_kw={"placeholder": "Enter your username"}
    )
    email = StringField(
        'Email',
        validators=[DataRequired(), Email()],
        render_kw={"placeholder": "Enter your email address"}
    )
    password = PasswordField(
        'Password',
        validators=[DataRequired(), Length(min=6)],
        render_kw={"placeholder": "Enter your password"}
    )
    confirm_password = PasswordField(
        'Confirm Password',
        validators=[DataRequired(), EqualTo('password', message="Passwords must match")],
        render_kw={"placeholder": "Confirm your password"}
    )
    submit = SubmitField('Register')
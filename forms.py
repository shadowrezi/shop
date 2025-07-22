import re

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email, Length, EqualTo, ValidationError


class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=32)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[
        DataRequired(),
        Length(min=8, message='Password must contain at least 9 symbols')
    ])
    confirm = PasswordField('Confirm Password', validators=[
        DataRequired(),
        EqualTo('password', message="Passwords don't match")
    ])
    submit = SubmitField('Register')

    def validate_password(self, field):
        if not re.search(r"[A-Z]", field.data):
            raise ValidationError('The password must contain at least one capital letter.')
        if not re.search(r"\d", field.data):
            raise ValidationError('The password must contain at least one number.')

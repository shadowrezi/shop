import re

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, EmailField
from wtforms.validators import DataRequired, Email, Length, EqualTo, ValidationError


class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=6, max=32)])
    email = EmailField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[
        DataRequired(),
        Length(min=8, message='Password must contain at least 8 symbols')
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


class LogInForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=6, max=32)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=8, max=32, message='Password must contain from 8 to 32 symbols')])

    submit = SubmitField('Log in')
    
    
class CodeVerificationForm(FlaskForm):
    code = StringField(
        "Enter verification code",
        validators=[
            DataRequired(),
            Length(min=4, max=4)
        ]
    )
    submit = SubmitField('Verify')


class ChangePasswordForm(FlaskForm):
    old_password = PasswordField(
        'Old password',
        validators=[
            DataRequired(),
            Length(min=8)
        ]
    )
    new_password = PasswordField(
        'New password',
        validators=[
            DataRequired(),
            Length(min=8)
        ]
    )
    confirm_password = PasswordField(
        'Confirm password',
        validators=[
            DataRequired(),
            EqualTo('new_password', message='Passwords must match')
        ]
    )
    submit = SubmitField('Change Password')

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, EmailField, DecimalField
from wtforms.validators import DataRequired, Email, Length, EqualTo, NumberRange


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


class WithdrawForm(FlaskForm):
    amount = DecimalField(
        'Sum (UAH)',
        validators=[
            DataRequired(),
            NumberRange(min=100, message='Minimal sum must be at least 100 UAH')
        ]
    )
    details = StringField(
        'details (card number)',
        validators=[
            DataRequired(),
            Length(min=16, max=128)
        ]
    )
    submit = SubmitField('Withdraw')

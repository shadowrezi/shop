import re
from random import randint
import threading

from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from flask_login import login_user, logout_user, current_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash

from common.forms import RegistrationForm, CodeVerificationForm, LogInForm, ChangePasswordForm
from common.models import db, User
from common.send_email import send_email

auth = Blueprint('auth', __name__)


def validate_password(password: str) -> list[str]:
    errors = []
    if not re.search(r"[A-Z]", password):
        errors.append(['The password must contain at least one capital letter.', 'warning'])

    if not re.search(r"\d", password):
        errors.append(['The password must contain at least one number.', 'warning'])

    if re.search(r'\s', password):
        errors.append(['The password may not contain spaces', 'warning'])

    return errors


def print_errors(errors: list[str] | list[list[str]]) -> None:
    for error in errors:
        if isinstance(error, str):
            flash(error)
        elif isinstance(error, list) and len(error) == 2:
            flash(*error)
        else:
            flash('An unknown error occurred', 'danger')


@auth.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()

    if form.validate_on_submit():
        username = form.username.data.strip()
        email = form.email.data.strip()
        password = form.password.data.strip()

        errors = []

        if User.query.filter_by(username=username).first():
            errors.append('Account with this username has been already registered! ')
        if User.query.filter_by(email=email).first():
            errors.append('Account with this email has been already registered!')
        
        errors.extend(
            validate_password(password)
        )

        if errors:
            print_errors(errors)
            return render_template('register.html', form=form)

        code = str(randint(1000, 9999))
        session['registration'] = {
            'username': username,
            'email': email,
            'password': generate_password_hash(password),
            'code': code
        }

        html = f'<h2>Your Verification Code: </h2><h1><b>{code}</b></h1>'
        threading.Thread(target=send_email, args=(email, 'Verification code', html)).start()
        flash('We sent verification code on your email.')
        return redirect(url_for('auth.verify'))
    return render_template('register.html', form=form)


@auth.route('/verify', methods=['GET', 'POST'])
def verify():
    form = CodeVerificationForm()
    register_data = session.get('registration')

    if not register_data:
        flash('Session is deprecated! Try again', 'warning')
        return redirect(url_for('auth.register'))

    if form.validate_on_submit():
        if form.code.data.strip() == register_data['code']:
            user = User(
                username=register_data['username'],
                email=register_data['email'],
                password=register_data['password'],
                balance=300
            )
            db.session.add(user)
            db.session.commit()

            session.pop('registration')
            flash('Registration is successful!', 'success')
            login_user(user)
            return redirect(url_for('main.index'))
        else:
            flash("Invalid code!")
    return render_template('verify.html', form=form)


@auth.route('/login', methods=['GET', 'POST'])
def login():
    form = LogInForm()

    if request.method == 'POST':
        login_data = form.username.data.strip()
        password = form.password.data.strip()

        user = User.query.filter((User.username == login_data) | (User.email == login_data)).first()

        if not user:
            flash("User not found")
            return render_template('login.html', form=form)

        if check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('main.index'))
        flash("Password is incorrect", 'danger')
    return render_template('login.html', form=form)


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.index'))


@auth.route('/change_password', methods=['GET', 'POST'])
@login_required
def change_password():
    form = ChangePasswordForm()
    if form.validate_on_submit():
        old_password = form.old_password.data
        new_password = form.new_password.data
        
        errors = validate_password(new_password)
        
        if errors:
            print_errors(errors)
            return render_template('change_password.html', form=form)

        if check_password_hash(current_user.password, old_password):
            current_user.password = generate_password_hash(new_password)
            db.session.commit()
            flash('Password updated successfully!', 'success')
            return redirect(url_for('main.profile'))
        else:
            flash('Old password is incorrect!', 'danger')
    return render_template('change_password.html', form=form)

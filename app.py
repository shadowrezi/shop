from random import randint

from flask import Flask, render_template, redirect, url_for, request, flash, session
from flask_login import LoginManager, login_required, login_user, logout_user, current_user

from werkzeug.security import generate_password_hash
from itsdangerous import URLSafeTimedSerializer

from send_email import send_email
from config import Config
from models import db, User, Product, Purchase
from forms import RegistrationForm, CodeVerificationForm


app = Flask(__name__)
app.secret_key = Config.SECRET_KEY
app.config['SQLALCHEMY_DATABASE_URI'] = Config.SQLALCHEMY_DATABASE_URI

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

db.init_app(app)

s = URLSafeTimedSerializer(app.config['SECRET_KEY'])


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


with app.app_context():
    db.create_all()
    if not Product.query.first():
        product = Product(
            name='',
            price=1,
            payment_id='kvmaa'
        )
        db.session.add(product)
        db.session.commit()


@app.route('/')
def index():
    products = Product.query.all()
    return render_template('index.html', products=products)


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        username = form.username.data.strip()
        email = form.email.data.strip()
        password = form.password.data.strip()
        
        if User.query.filter_by(username=username).first():
            flash('Account with this username has been already registered!')
        if User.query.filter_by(email=email).first():
            flash('Account with this email has been already registered!')

        code = str(randint(1000, 9999))
        session['registration'] = {
            'username': username,
            'email': email,
            'password': generate_password_hash(password),
            'code': code
        }
        
        html = f'''
            <h2>Your Verification Code: </h2>
            <h1><b>{code}</b></h1>
        '''
        
        send_email(email, 'Verification code', html)
        flash('We sent verification code on your email. ')
        return redirect(url_for('verify'))
    return render_template('register.html', form=form)


@app.route('/verify', methods=['GET', 'POST'])
def verify():
    form = CodeVerificationForm()
    register_data = session.get('registration')
    
    if not register_data:
        flash('Session is deprecated! Try again')
        return redirect(url_for('register'))
    
    if form.validate_on_submit() and form.code.data.strip() == register_data['code']:
        user = User(
            username=register_data['username'],
            email=register_data['email'],
            password=register_data['password']
        )
        db.session.add(user)
        db.session.commit()
        
        session.pop('registration')
        flash('Registration is successfuly! ')
        return redirect(url_for('login'))
    
    flash("Invalid code! ")
    return render_template('verify.html', form=form)
        

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        user = User.query.filter_by(username=username).first()
        if user:
            login_user(user)
            return redirect(url_for('index'))
        flash('Користувача не знайдено.')
    return render_template('login.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/profile')
@login_required
def profile():
    return render_template('profile.html', user=current_user)


@app.route('/buy/<int:product_id>')
@login_required
def buy_product(product_id):
    product = Product.query.get_or_404(product_id)
    return redirect(f'https://urijozimko.gumroad.com/l/{product.payment_id}')


@app.route('/gumroad_webhook', methods=['POST'])
def payment_success():
    data = request.form.to_dict()
    payment_id = data['permalink']
    email = data['email']
    
    product = Product.query.filter_by(payment_id=payment_id).first()
    user = User.query.filter_by(email=email).first()
    
    purchase = Purchase(user_id=user.id, product_id=product.id)

    db.session.add(purchase)
    db.session.commit()
    
    flash(f'{product.name} purchased!')
    
    return redirect(url_for('profile'))


if __name__ == '__main__':
    app.run(debug=True)

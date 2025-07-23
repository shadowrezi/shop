from flask import Flask, render_template, redirect, url_for, request, flash, abort
from flask_login import LoginManager, login_required, login_user, logout_user, current_user

from werkzeug.security import generate_password_hash
from itsdangerous import URLSafeTimedSerializer

from send_email import send_email
from config import Config
from models import db, User, Product, Purchase
from forms import RegistrationForm


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
        email = form.email.data.strip()
        username = form.username.data.strip()
        hashed_password = generate_password_hash(form.password.data)
        
        if User.query.filter_by(username=username).first():
            flash('Username is not avaible.')
            return redirect(url_for('register'))
        if User.query.filter_by(email=email).first():
            flash('Email is not avaible')
            return redirect(url_for('register'))
    
        user = User(username=username, email=email, password=hashed_password, confirmed=False)
        db.session.add(user)
        db.session.commit()
        
        token = s.dumps(user.email, salt='email-confirm')
        confirm_url = url_for('confirm_email', token=token, _external=True)
        html = render_template('email_confirmation.html', confirm_url=confirm_url)
        send_email(user.email, 'Confirm email', html)
        print(html)
        
        flash('Check your email for confirm account')
        return redirect(url_for('login'))
    return render_template('register.html', form=form)


@app.route('/confirm/<token>')
def confirm_email(token):
    try:
        email = s.loads(token, salt='email-confirm', max_age=3600)
    except Exception:
        flash('Посилання недійсне або прострочене.', 'danger')
        return redirect(url_for('register'))

    user = User.query.filter_by(email=email).first_or_404()
    if user.confirmed:
        flash('Email вже підтверджений.', 'info')
    else:
        user.confirmed = True
        db.session.commit()
        flash('Email успішно підтверджено.', 'success')

    return redirect(url_for('index'))


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


@app.route('/payment_success/<int:product_id>', methods=['POST'])
@login_required
def payment_success(product_id: int):
    
    status = request.form.get('transactionStatus')
    reason_code = request.form.get('reasonCode')
    
    if status != 'Approved' or reason_code != '1100':
        abort(403)

    product = Product.query.get_or_404(product_id)
    
    purchase = Purchase(user_id=current_user.id, product_id=product.id)
    db.session.add(purchase)
    db.session.commit()
    
    flash(f'Покупка товара "{product.name}" успешна!')
    
    return redirect(url_for('profile'))


@app.route('/gumroad_webhook', methods=['POST'])
def catch_all():
    data = request.form.to_dict()
    payment_id = data['payment_id']
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

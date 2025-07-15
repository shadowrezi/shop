from flask import Flask, render_template, redirect, url_for, request, flash, abort
from flask_login import LoginManager, login_required, login_user, logout_user, current_user
from models import db, User, Product, Purchase

app = Flask(__name__)
app.secret_key = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///shop.db'

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

db.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


with app.app_context():
    db.create_all()
    if not Product.query.first():
        product = Product(
            name='',
            price=100.0,
            payment_url='https://secure.wayforpay.com/button/b92b81655ead9'
        )
        db.session.add(product)
        db.session.commit()


@app.route('/')
def index():
    products = Product.query.all()
    return render_template('index.html', products=products)


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        if User.query.filter_by(username=username).first():
            flash('Користувач вже існує.')
            return redirect(url_for('register'))
        user = User(username=username)
        db.session.add(user)
        db.session.commit()
        login_user(user)
        return redirect(url_for('index'))
    return render_template('register.html')


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
    return redirect(product.payment_url)


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


if __name__ == '__main__':
    app.run(debug=True)

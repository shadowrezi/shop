import time
import hashlib
import base64

from flask import Flask, render_template, redirect, url_for, session, request, flash
from models import db, User, Product

app = Flask(__name__)
app.secret_key = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///shop.db'

db.init_app(app)

with app.app_context():
    db.create_all()
    
    product = Product(
        name='Перший товар',
        price=100.0,
        payment_url='https://secure.wayforpay.com/button/bf63b7694ad58'
    )
    db.session.add(product)
    db.session.commit()

MERCHANT_LOGIN = 'shop_auf1_onrender_com1'
MERCHANT_SECRET_KEY = '55221fdaae9c08a5c618d5bbd84556b2317aac7b'
MERCHANT_PASSWORD = '4562bd8b7dc5cbedfe5ad6265c0dc5f2'
DOMAIN = "https://shop-auf1.onrender.com"


def generate_signature(params: list, secret_key: str) -> str:
    raw = ';'.join([str(p) for p in params])
    hashed = hashlib.sha1(raw.encode()).digest()
    return base64.b64encode(hashed).decode()


@app.route('/')
def index():
    products = Product.query.all()
    user = None
    if 'user_id' in session:
        user = User.query.get(session['user_id'])
    return render_template('index.html', products=products, user=user)


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
        session['user_id'] = user.id
        return redirect(url_for('index'))
    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        user = User.query.filter_by(username=username).first()
        if user:
            session['user_id'] = user.id
            return redirect(url_for('index'))
        flash('Користувача не знайдено.')
    return render_template('login.html')


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))


@app.route('/profile')
def profile():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    user = User.query.get(session['user_id'])
    return render_template('profile.html', user=user)


@app.route('/buy/<int:product_id>')
def buy(product_id: int):
    product = Product.query.get(product_id)
    if not product:
        flash('Product not found! ')
        return render_template("index.html")
    
    order_id = f"ORDER_{int(time.time())}"
    order_date = int(time.time())
    
    params = [
        "shop_auf1_onrender_com1",
        DOMAIN,
        order_id,
        order_date,
        f'{product.price:.2f}',
        "UAH",
        [],
        "1",
        f'{product.price:.2f}'
    ]
    
    signature = generate_signature(params, secret_key=MERCHANT_SECRET_KEY)

    return render_template("buy.html", **{
        "merchantAccount": MERCHANT_LOGIN,
        "merchantDomainName": DOMAIN,
        "orderReference": order_id,
        "orderDate": order_date,
        "amount": f'{product.price:.2f}',
        "productName": [],
        "signature": signature,
        "productId": product_id
    })


@app.route('/payment_callback', methods=['POST'])
def payment_callback():
    data = request.json
    
    print(data)
    return "OK"


@app.route('/payment_success/<int:product_id>')
def payment_success(product_id: int):
    print(product_id)


if __name__ == '__main__':
    app.run(debug=True)

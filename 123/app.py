from flask import (
    Flask, render_template, redirect,
    url_for, request, session, flash
)
from werkzeug.security import (
    generate_password_hash, check_password_hash
)
from database import db
from models import User, Product, Purchase


app = Flask(__name__)
app.secret_key = '123'

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///shop.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)


@app.before_request
def create_tables():
    db.create_all()

    if not Product.query.first():
        sample_products = [
            Product(
                name="Книга",
                price=150,
                description="Цікава книга."
            ),
            Product(
                name="Навушники",
                price=300,
                description="З якісним звуком."
            )
        ]
        db.session.add_all(sample_products)
        db.session.commit()


@app.route('/')
def index():
    products = Product.query.all()
    user = None

    if session.get('user_id'):
        user = User.query.get(session['user_id'])  # <-- завжди свіже

    return render_template(
        'index.html',
        products=products,
        user=user
    )


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = generate_password_hash(request.form['password'])

        if User.query.filter_by(username=username).first():
            flash('Користувач вже існує.')
            return redirect(url_for('register'))

        new_user = User(
            username=username,
            password=password
        )

        db.session.add(new_user)
        db.session.commit()

        flash('Реєстрація успішна. Увійдіть.')
        return redirect(url_for('login'))

    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = User.query.filter_by(
            username=request.form['username']
        ).first()

        if user and check_password_hash(
            user.password, request.form['password']
        ):
            session['user_id'] = user.id
            flash('Успішний вхід.')
            return redirect(url_for('index'))

        flash('Невірний логін або пароль.')

    return render_template('login.html')


@app.route('/logout')
def logout():
    session.pop('user_id', None)
    flash('Ви вийшли.')
    return redirect(url_for('index'))


@app.route('/buy/<int:product_id>')
def buy(product_id):
    user_id = session.get('user_id')

    if not user_id:
        flash("Авторизуйтесь для покупки")
        return redirect(url_for('login'))

    user = User.query.get(user_id)
    product = Product.query.get(product_id)

    if product is None:
        flash("Товар не знайдено")
        return redirect(url_for('index'))

    if user.balance < product.price:
        flash("Недостатньо коштів")
        return redirect(url_for('index'))

    # Списати гроші, зберегти покупку
    user.balance -= product.price

    purchase = Purchase(
        user_id=user.id,
        product_id=product.id
    )

    db.session.add(purchase)
    db.session.commit()

    flash(f"Товар '{product.name}' куплено!")
    return redirect(url_for('index'))


@app.route('/profile')
def profile():
    user_id = session.get('user_id')

    if not user_id:
        flash("Спочатку увійдіть")
        return redirect(url_for('login'))

    user = User.query.get(user_id)

    purchases = Purchase.query.filter_by(
        user_id=user.id
    ).all()

    bought_products = [p.product for p in purchases]

    return render_template(
        'profile.html',
        user=user,
        products=bought_products
    )


#if __name__ == '__main__':
#    app.run(host='0.0.0.0', port=5000, debug=True)
 
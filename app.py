from flask import Flask, render_template, redirect, url_for, session, request, flash
from models import db, User, Product

app = Flask(__name__)
app.secret_key = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///shop.db'

db.init_app(app)

with app.app_context():
    db.create_all()


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


@app.route('/confirm_payment')
def confirm_payment():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    user = User.query.get(session['user_id'])

    # (опціонально) додай логіку додавання товару вручну тут
    flash('Платіж підтверджено. Дякуємо за покупку!')
    return redirect(url_for('profile'))


if __name__ == '__main__':
    app.run(debug=True)

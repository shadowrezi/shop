from flask import Flask, render_template
from flask_login import LoginManager

from common.models import db, User, Product

from routes.main import main
from routes.auth import auth
from routes.shop import shop
from routes.withdraw import withdraw


app = Flask(__name__)
app.secret_key = 'shadow'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///shop.db'

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'auth.login'

db.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


with app.app_context():
    db.create_all()
    
    # from random import randint
    # for i in range(10):
    if not Product.query.first():
        product = Product(
            name='asd s',
            price=1,
            payment_id='kvmaa',
            description='dasdsa asd a sdas d'
        )
        db.session.add(product)
        db.session.commit()


app.register_blueprint(main)
app.register_blueprint(auth)
app.register_blueprint(shop)
app.register_blueprint(withdraw)

if __name__ == '__main__':
    app.run(debug=True)

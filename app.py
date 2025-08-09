from flask import Flask, render_template
from flask_login import LoginManager

from werkzeug.security import generate_password_hash

from common.models import db, User, Product

from routes.main import main
from routes.auth import auth
from routes.shop import shop
from routes.wallet import wallet
from routes.admin import admin


app = Flask(__name__)
app.secret_key = 'shadow'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///shop.db'

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'auth.login'

db.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


with app.app_context():
    db.create_all()

    if not db.session.query(Product).first():
        product = Product(
            name='asd s',
            price=1,
            description='dasdsa asd a sdas d'
        )
        db.session.add(product)
        db.session.commit()
    
    if not db.session.query(User).first():
        user = User(
            username='admin1',
            email='urijozimko4@gmail.com',
            password=generate_password_hash('adminadmin'),
            is_admin=True
        )
        db.session.add(user)
        db.session.commit()


app.register_blueprint(main)
app.register_blueprint(auth)
app.register_blueprint(shop)
app.register_blueprint(wallet)
app.register_blueprint(admin)


if __name__ == '__main__':
    app.run(debug=True)

from flask import Flask
from flask_login import LoginManager

from common.models import db, User, Product

from routes.main import main
from routes.auth import auth
from routes.shop import shop


app = Flask(__name__)
app.secret_key = 'shadow'
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
            name='dasads ',
            price=1,
            payment_id='kvmaa',
            description='dasdsa asd a sdas d'
        )
        db.session.add(product)
        db.session.commit()


app.register_blueprint(main)
app.register_blueprint(auth)
app.register_blueprint(shop)
    
if __name__ == '__main__':
    app.run(debug=True)

from flask import Blueprint, render_template
from flask_login import login_required, current_user

from common.models import Product


main = Blueprint('main', __name__)


@main.route('/')
def index():
    products = Product.query.all()
    return render_template('index.html', products=products)


@main.route('/profile')
@login_required
def profile():
    return render_template('user/profile.html', user=current_user, hide_footer=True)

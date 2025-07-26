from flask import Blueprint, render_template, redirect, url_for, request, flash, abort
from flask_login import login_required

from common.models import Product, Purchase, User, db

shop = Blueprint('shop', __name__)


@shop.route('/products/<int:page>')
def products(page: int):
    per_page = 20
    total = Product.query.count()
    total_pages = (total // per_page) + 1

    if page < 1 or page > total_pages:
        abort(404)

    products = Product.query.offset((page - 1) * per_page).limit(per_page).all()

    return render_template('products.html', products=products, page=page, total_pages=total_pages)


@shop.route('/products')
def products_redirect():
    return redirect(url_for('shop.products', page=1))


@shop.route('/product/<int:product_id>')
def product_card(product_id: int):
    product = Product.query.get_or_404(product_id)
    return render_template('product.html', product=product)


@shop.route('/buy/<int:product_id>')
@login_required
def buy_product(product_id: int):
    product = Product.query.get_or_404(product_id)
    return redirect(f'https://urijozimko.gumroad.com/l/{product.payment_id}')


@shop.route('/gumroad_webhook', methods=['POST'])
def payment_success():
    data = request.form.to_dict()
    payment_id = data['permalink']
    email = data['email']

    product = Product.query.filter_by(payment_id=payment_id).first()
    user = User.query.filter_by(email=email).first()

    if product and user:
        if not Purchase.query.filter_by(user_id=user.id, product_id=product.id).first():
            purchase = Purchase(user_id=user.id, product_id=product.id)
            db.session.add(purchase)
            db.session.commit()
            flash(f'{product.name} purchased!')

    return redirect(url_for('main.profile'))

from flask import Blueprint, render_template, redirect, url_for, flash, abort
from flask_login import current_user, login_required

from common.models import Product, Purchase, db

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
    
    if product.price > current_user.balance:
        flash('Insufficient funds to buy this product', 'warning')
        return redirect(url_for('shop.product_card', product_id=product_id))
    
    purchase = Purchase(user_id=current_user.id, product_id=product.id)
    current_user.balance -= product.price

    db.session.add(purchase)
    db.session.commit()
    
    flash(f'You have successfully purchased {product.name}!', 'success')

    return redirect(url_for('main.profile'))

from functools import wraps

from flask import Blueprint, render_template, redirect, request, url_for, flash
from flask_login import current_user

from common.models import Product, Purchase, User, WalletRequest, db
from common.forms import AddProductForm

admin = Blueprint('admin', __name__, url_prefix='/admin')


def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('You need to log in first.', 'warning')
            return redirect(url_for('auth.login'))
        if not current_user.is_admin:
            flash('You do not have permission to access this page.', 'danger')
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    return decorated_function


@admin.route('/')
@admin_required
def index():
    stats = {
        'users': User.query.count(),
        'products': Product.query.count(),
        'wallet_requests': WalletRequest.query.count(),
        'purchases': Purchase.query.count()
    }
    return render_template('admin/index.html', stats=stats)


@admin.route('/products')
@admin_required
def products():
    products = Product.query.all()
    return render_template('admin/products.html', products=products)


@admin.route('/products/add', methods=['GET', 'POST'])
@admin_required
def add_product():
    form = AddProductForm()
    
    if request.method == 'POST':
        name = request.form['name']
        price = float(request.form['price'])
        description = request.form['description']
        
        new_product = Product(name=name, price=price, description=description)
        db.session.add(new_product)
        db.session.commit()
        flash('Product added successfully.')
        return redirect(url_for('admin.products'))

    return render_template('admin/add_product.html', form=form)


@admin.route('/products/delete/<int:product_id>', methods=['POST'])
@admin_required
def delete_product(product_id):
    product = Product.query.get_or_404(product_id)
    db.session.delete(product)
    db.session.commit()
    flash("Product deleted.", "warning")
    return redirect(url_for('admin.products'))

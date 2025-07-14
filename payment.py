import base64
import hashlib
import hmac
import json
import time

from flask import Blueprint, render_template, request, redirect, session, url_for, flash
from models import db, User, Product, Purchase

payment_bp = Blueprint('payment', __name__)

# === CONFIG ===
MERCHANT_ACCOUNT = '4d14a797c3aa67cad4be8adb4de473fd341c88e0'
MERCHANT_SECRET_KEY = '6ffc18fde19eb25c7720f3fec57309aa'

MERCHANT_DOMAIN = 'shop-auf1.onrender.com'
RETURN_URL = 'https://shop-auf1.onrender.com/payment/success'
CURRENCY = 'UAH'


# === HELPER: підпис ===
def generate_signature(data: dict) -> str:
    keys = [
        'merchantAccount', 'merchantDomainName', 'orderReference', 'orderDate',
        'amount', 'currency', 'productName', 'productCount', 'productPrice'
    ]

    message = ';'.join(
        str(data[key]) if not isinstance(data[key], list)
        else ','.join(map(str, data[key]))
        for key in keys
    )

    return base64.b64encode(
        hmac.new(MERCHANT_SECRET_KEY.encode(), message.encode(), hashlib.md5).digest()
    ).decode()


# === PAGE: ініціація платежу ===
@payment_bp.route('/pay/<int:product_id>')
def pay(product_id):
    user_id = session.get('user_id')
    if not user_id:
        flash('Потрібно увійти для покупки.')
        return redirect(url_for('login'))

    user = User.query.get(user_id)
    product = Product.query.get(product_id)

    if not product:
        flash('Товар не знайдено.')
        return redirect(url_for('index'))

    order_reference = f"ORDER-{user.id}-{product.id}-{int(time.time())}"
    order_date = int(time.time())

    payment_data = {
        'merchantAccount': MERCHANT_ACCOUNT,
        'merchantDomainName': MERCHANT_DOMAIN,
        'orderReference': order_reference,
        'orderDate': order_date,
        'amount': product.price,
        'currency': CURRENCY,
        'productName': [product.name],
        'productCount': [1],
        'productPrice': [product.price],
        'returnUrl': RETURN_URL,
    }

    payment_data['merchantSignature'] = generate_signature(payment_data)

    return render_template('pay.html', payment=payment_data)


# === CALLBACK: підтвердження платежу ===
@payment_bp.route('/payment/callback', methods=['POST'])
def payment_callback():
    data = request.get_json()

    received_signature = data.get('merchantSignature')
    expected_signature = generate_signature({
        'merchantAccount': data['merchantAccount'],
        'merchantDomainName': data['merchantDomainName'],
        'orderReference': data['orderReference'],
        'orderDate': data['orderDate'],
        'amount': data['amount'],
        'currency': data['currency'],
        'productName': data['productName'],
        'productCount': data['productCount'],
        'productPrice': data['productPrice'],
    })

    if received_signature != expected_signature:
        return 'Invalid signature', 403

    if data.get('transactionStatus') == 'Approved':
        order_reference = data['orderReference']
        parts = order_reference.split('-')

        try:
            user_id = int(parts[1])
            product_id = int(parts[2])
        except (IndexError, ValueError):
            return 'Invalid orderReference format', 400

        user = User.query.get(user_id)
        product = Product.query.get(product_id)

        if user and product:
            existing = Purchase.query.filter_by(user_id=user.id, product_id=product.id).first()
            if not existing:
                purchase = Purchase(user_id=user.id, product_id=product.id)
                db.session.add(purchase)
                db.session.commit()

    return json.dumps({'orderReference': data['orderReference'], 'status': 'accept'}), 200


# === PAGE: після повернення з платіжки ===
@payment_bp.route('/payment/success')
def payment_success():
    flash('Оплата пройшла успішно! Товар додано до вашого профілю.')
    return redirect(url_for('index'))

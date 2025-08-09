from os import getenv
import requests

from flask import Blueprint, jsonify, render_template, request, flash, redirect, url_for, abort
from flask_login import login_required, current_user

from dotenv import load_dotenv

from common.models import User, db, WalletRequest
from common.forms import WithdrawForm, TopupForm


load_dotenv('.env')

TELEGRAM_TOKEN = getenv('TELEGRAM_TOKEN')
ADMIN_CHAT_ID = getenv('ADMIN_CHAT_ID')
URL = f'https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage'

wallet = Blueprint('wallet', __name__)


@wallet.route('/wallet/withdraw', methods=['GET', 'POST'])
@wallet.route('/wallet/topup', methods=['GET', 'POST'])
@login_required
def request_wallet():
    action = request.path.split('/')[-1]
    if action == 'withdraw':
        form = WithdrawForm()
    elif action == 'topup':
        form = TopupForm()
    else:
        abort(404)
    
    if form.validate_on_submit():
        amount = float(request.form.get('amount'))
        details = request.form.get('details')

        if action == 'withdraw':
            if amount > current_user.balance:
                flash('Insufficient funds for withdraw', 'warning')
                return render_template('withdraw.html', form=form)

            current_user.balance -= amount
        elif action == 'topup':
            ...
        
        wallet_request = WalletRequest(
            user_id=current_user.id,
            type=action,
            amount=amount,
            details=details
        )
        db.session.add(wallet_request)
        db.session.commit()
        
        message = f'''
🔔 *{action.capitalize()} request*
👤 User: {current_user.username} (ID: {current_user.id})
💳 Datails: {details}
💰 Sum: {amount:.2f} UAH
        '''.strip()

        data = {
            'chat_id': ADMIN_CHAT_ID,
            'text': message,
            'parse_mode': 'Markdown',
            'reply_markup': {
                'inline_keyboard': [[
                    {'text': '✅ Approve', 'callback_data': f'approve:{wallet_request.id}'},
                    {'text': '❌ Decline', 'callback_data': f'decline:{wallet_request.id}'}
                ]]
            }
        }
        try:
            r = requests.post(URL, json=data)
            print(r.text)
            flash(f'{action.capitalize()} requested! ', 'success')
        except Exception as ex:
            flash('Error, try again! ', 'warning')
            print(ex)
        return redirect(url_for('wallet.history'))
    return render_template(f'{action}.html', form=form)


@wallet.route('/wallet/request/<action>', methods=['POST'])
def update_request(action: str):
    data = request.get_json()
    request_id = data.get('request_id')
    reason = data.get('reason')

    wallet_request = db.session.get(WalletRequest, request_id)
    if not wallet_request:
        return jsonify({'error': 'Request not found'}), 404

    if wallet_request.status != 'pending':
        return jsonify({'error': 'Request already processed'}), 400

    type = wallet_request.type
    if type not in ('withdraw', 'topup'):
        return jsonify({'error': 'Invalid request type'}), 400
    
    current_user = db.session.get(User, wallet_request.user_id)

    if type == 'withdraw' and action == 'decline':
        current_user.balance += wallet_request.amount
    elif type == 'topup' and action == 'approve':
        current_user.balance += wallet_request.amount
    wallet_request.status = action
    wallet_request.reason = reason if reason else None
    db.session.commit()

    return jsonify({'status': 200})


@wallet.route('/wallet/history')
@login_required
def history():
    requests = WalletRequest.query.filter_by(user_id=current_user.id).order_by(WalletRequest.created_at.desc()).all()
    return render_template('history.html', requests=requests)

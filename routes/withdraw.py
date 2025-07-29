from os import getenv
import requests

from flask import Blueprint, jsonify, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user

from dotenv import load_dotenv

from common.models import db, WithdrawRequest
from common.forms import WithdrawForm


load_dotenv('.env')

TELEGRAM_TOKEN = getenv('TELEGRAM_TOKEN')
ADMIN_CHAT_ID = getenv('ADMIN_CHAT_ID')

withdraw = Blueprint('withdraw', __name__)


@withdraw.route('/withdraw', methods=['GET', 'POST'])
@login_required
def send_withdraw_telegram():
    form = WithdrawForm()
    if form.validate_on_submit():
        amount = float(request.form.get('amount'))
        details = request.form.get('details')

        if amount > current_user.balance:
            flash('Insufficient funds for withdraw', 'warning')
            return render_template('withdraw.html', form=form)

        current_user.balance -= amount

        withdraw = WithdrawRequest(
            user_id=current_user.id,
            amount=amount,
            details=details
        )
        db.session.add(withdraw)
        db.session.commit()
        
        message = f'''
🔔 *Withdraw request*
👤 User: {current_user.username} (ID: {current_user.id})
💳 Datails: {details}
💰 Sum: {amount:.2f} UAH
        '''.strip()

        url = f'https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage'
        data = {
            'chat_id': ADMIN_CHAT_ID,
            'text': message,
            'parse_mode': 'Markdown',
            'reply_markup': {
                'inline_keyboard': [[
                    {'text': '✅ Approve', 'callback_data': f'approve:{withdraw.id}'},
                    {'text': '❌ Decline', 'callback_data': f'decline:{withdraw.id}'}
                ]]
            }
        }
        try:
            r = requests.post(url, json=data)
            print(r.text)
            flash('Withdraw requested! ', 'success')
        except Exception as ex:
            flash('Error, try again! ', 'warning')
            print(ex)
        return redirect(url_for('withdraw.history'))
    return render_template('withdraw.html', form=form)


@withdraw.route('/withdraw/history')
@login_required
def history():
    withdraws = WithdrawRequest.query.filter_by(user_id=current_user.id).order_by(WithdrawRequest.created_at.desc()).all()
    return render_template('withdraws_history.html', withdraws=withdraws)


@withdraw.route('/withdraw/<action>', methods=['POST'])
def update_withdraw(action: str):
    data = request.get_json()
    withdraw_id = data.get('withdraw_id')
    reason = data.get('reason')
    
    if action not in ('approve', 'decline'):
        return jsonify({'error': 'Invalid action'}), 400

    withdraw_request = db.session.get(WithdrawRequest, withdraw_id)
    if not withdraw_request:
        return jsonify({'error': 'Withdrawal request not found'}), 404

    if withdraw_request.status != 'pending':
        return jsonify({'error': 'Request already processed'}), 400

    if action == 'decline':
        current_user.balance += withdraw_request.amount

    withdraw_request.status = action
    withdraw_request.reason = reason if reason else None

    db.session.commit()

    return jsonify({'status': 200})

import random
import string
from datetime import timedelta, datetime

from flask import Blueprint, render_template, session, jsonify, request
from flask_login import login_required, current_user

from common.models import db, User

telegram = Blueprint('telegram', __name__)

active_tokens = {}


def generate_token():
    chars = string.ascii_uppercase + string.digits
    part1 = ''.join(random.choices(chars, k=4))
    part2 = ''.join(random.choices(chars, k=4))
    return f"{part1}-{part2}"


@telegram.route('/telegram/connect')
@login_required
def get_token():
    token_time = session.get('telegram_token_time')
    if not token_time or (datetime.utcnow() - datetime.fromisoformat(token_time)) > timedelta(minutes=1):
        session['telegram_token'] = generate_token()
        print(active_tokens)
        session['telegram_token_time'] = datetime.utcnow().isoformat()
        active_tokens[session['telegram_token']] = current_user.id
    return render_template('connect_telegram.html', token=session['telegram_token'])


@telegram.route('/telegram/api/link', methods=['POST'])
def connect():
    data = request.get_json()
    token = data.get('token')
    chat_id = data.get('chat_id')
    
    if not token or token not in active_tokens:
        return jsonify({'status': 'error', 'message': 'Invalid token'}), 400
    
    user_id = active_tokens[token]
    user = User.query.get(user_id)
    if not user:
        return jsonify({'status': 'error', 'message': 'User not found'}), 400
    
    user.telegram_id = chat_id
    db.session.commit()
    
    del active_tokens[token]
    
    return jsonify({'status': 'ok'})

from flask import Blueprint, request, jsonify
from flask_login import login_user, login_required, current_user, logout_user

from webservice import db
from webservice.schemes import user_schema
from webservice.models import Users

from werkzeug.security import check_password_hash

from datetime import datetime


auth = Blueprint('auth', __name__)

@auth.route('/api/login/', methods=['POST'])
def login():
    if current_user.is_authenticated:
        return jsonify({'detail': 'You are already logged in'}), 200

    data = user_schema.loads(request.data)
    user = db.session.query(Users).filter(Users.email == data['email']).first()

    code = 403

    if user:
        if check_password_hash(user.password, data['password']):
            user.last_login = datetime.now()
            db.session.commit()

            login_user(user)
            return {'detail': 'Logged In'}, 200
        code = 401
    return jsonify({'detail': 'Invalid Credential'}), code


@auth.route('/api/logout/', methods=['POST'])
@login_required
def logout():
    db.session.query(Users).filter(Users.id == current_user().id).update({'logged_out': True})
    res = logout_user()
    if res:
        return jsonify({'detail': 'Logged out'}), 200
    return jsonify({'detail': 'A problem has occurred'}), 400

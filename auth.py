import os

from flask import Blueprint, request, jsonify, current_app, url_for, send_from_directory
from flask_login import login_user, login_required, current_user, logout_user
from werkzeug.utils import secure_filename

from webservice import db
from webservice.schemes import user_schema, projects_schema
from webservice.models import Users, Projects, UsersProjects

from werkzeug.security import check_password_hash

from datetime import datetime


auth = Blueprint('auth', __name__)


@auth.route('/api/login/', methods=['POST'])
def login():
    if current_user.is_authenticated:
        return jsonify({'detail': 'You are already logged in'}), 200

    data = user_schema.loads(request.data)
    user = db.session.query(Users).filter(Users.email == data['email'].lower()).first()

    code = 403

    if user:
        if check_password_hash(user.password, data['password']):
            user.last_login = datetime.now()
            db.session.commit()

            logged_in = login_user(user)
            if logged_in:
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


@auth.route('/api/check/')
@login_required
def check():
    return jsonify({}), 200


@auth.route('/uploads/<name>')
@login_required
def download_file(name):
    return send_from_directory(current_app.config["UPLOAD_FOLDER"], name)


@auth.route('/project', methods=['POST'])
@login_required
def new_project():
    data = {}

    for k, v in request.form.items():
        if k.startswith('user'):
            data.setdefault('users', []).append(v)
        else:
            data[k] = v

    for field, file_obj in request.files.items():
        filename = secure_filename(file_obj.filename)
        file_obj.save(os.path.join(current_app.config['UPLOAD_FOLDER'], filename))
        data[field] = url_for('auth.download_file', name=filename)

    users = data.pop('users', [])
    data = projects_schema.loads(
        projects_schema.dumps(data)
    )

    project = Projects(**data)
    project.user_projects.append(UsersProjects(user_id=1, is_owner=True))

    for user_id in users:
        project.user_projects.append(UsersProjects(user_id=user_id, is_owner=False))

    db.session.add(project)
    db.session.commit()

    return {}, 200

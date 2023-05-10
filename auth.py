import os

from flask import Blueprint, request, jsonify, current_app, url_for, send_from_directory
from flask_login import login_user, login_required, current_user, logout_user
from werkzeug.utils import secure_filename

from webservice import db
from webservice.gee import get_statistic
from webservice.schemes import user_schema, projects_schema, projects_read_schema, project_read_schema, query_schema
from webservice.models import Users, Projects, UsersProjects
from webservice.local import PLACEHOLDER_IMAGE

from werkzeug.security import check_password_hash

from datetime import datetime

import geopandas as gpd
import base64
import time

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
            user.logged_out = False
            db.session.commit()

            logged_in = login_user(user)
            if logged_in:
                return {'detail': 'Logged In'}, 200
        code = 401
    return jsonify({'detail': 'Invalid Credential'}), code


@auth.route('/api/logout/', methods=['POST'])
@login_required
def logout():
    db.session.query(Users).filter(Users.id == current_user.id).update({'logged_out': True})
    #db.session.query(Users).filter(Users.id == 1).update({'logged_out': True})
    res = logout_user()
    if res:
        return jsonify({'detail': 'Logged out'}), 200
    return jsonify({'detail': 'A problem has occurred'}), 400


@auth.route('/api/check/')
@login_required
def check():
    return jsonify({}), 200


@auth.route('/uploads/<name>/')
@login_required
def download_file(name):
    return send_from_directory(current_app.config["UPLOAD_FOLDER"], name)


@auth.route('/project/', methods=['POST'])
@login_required
def new_project():
    data = {}

    # (filed_name, alias_for_msg)
    required_fields = [
        ('name', 'name'),
        ('geo_data_file', 'Geo Data File'),
    ]

    for k, v in request.form.items():
        if k.startswith('user'):
            data.setdefault('users', []).append(v)
        else:
            data[k] = v

    for field, file_obj in request.files.items():
        data[field] = file_obj.filename

    for field in required_fields:
        if not data.get(field[0]):
            return {"detail": f'{field[1]} is required'}, 400

    for field, file_obj in request.files.items():
        filename = secure_filename(file_obj.filename)
        if filename:
            file_obj.save(os.path.join(current_app.config['UPLOAD_FOLDER'], filename))
            data[field] = url_for('auth.download_file', name=filename)
        else:
            data[field] = url_for('auth.download_file', name=PLACEHOLDER_IMAGE)

    users = data.pop('users', [])
    data = projects_schema.loads(
        projects_schema.dumps(data)
    )

    project = Projects(**data)
    project.users_projects.append(UsersProjects(user_id=1, is_owner=True))

    for user_id in users:
        project.users_projects.append(UsersProjects(user_id=user_id, is_owner=False))

    db.session.add(project)
    db.session.commit()

    return {'id': project.id}, 201


@auth.route('/api/projects/', methods=['GET'])
@login_required
def fetch_projects():
    projects = db.session.query(Projects).join(UsersProjects).filter(UsersProjects.user_id == current_user.id)
    #projects = db.session.query(Projects).join(UsersProjects).filter(UsersProjects.user_id == 1)
    return projects_read_schema.jsonify(projects), 200


@auth.route('/api/projects/<project_id>/', methods=['GET'])
@login_required
def fetch_project(project_id):
    project = db.session.query(Projects).join(UsersProjects) \
         .filter(UsersProjects.user_id == current_user.id, UsersProjects.project_id == project_id).first()
    #project = db.session.query(Projects).join(UsersProjects) \
    #    .filter(UsersProjects.user_id == 1, UsersProjects.project_id == project_id).first()
    return project_read_schema.jsonify(project), 200


@auth.route('/api/projects/<project_id>/', methods=['DELETE'])
@login_required
def delete_project(project_id):
    project = db.session.query(Projects).join(UsersProjects) \
         .filter(UsersProjects.user_id == current_user.id, UsersProjects.project_id == project_id).first()
    #project = db.session.query(Projects).join(UsersProjects) \
    #    .filter(UsersProjects.user_id == 1, UsersProjects.project_id == project_id).first()
    code = 403
    if project:
        db.session.delete(project)
        db.session.commit()
        code = 200
    return {}, code


@auth.route('/convert/', methods=['POST'])
@login_required
def convert():
    remote = request.args.get('remote', 0)

    if int(remote):
        file = request.form.get('file')
        if file:
            file = os.path.join(
                current_app.config["UPLOAD_FOLDER"],
                os.path.basename(file)
            )
    else:
        file = request.files.get('file')

    if not file:
        return {}, 400

    try:
        geojson = gpd.read_file(file)
        return geojson.to_json(), 200
    except Exception as e:
        return {'detail': 'failed to convert file'}, 400


@auth.route('/api/query/', methods=['POST'])
@login_required
def query():
    data = query_schema.loads(request.data)

    input_file = os.path.join(
        current_app.config["UPLOAD_FOLDER"],
        os.path.basename(data.url)
    )

    unique_name = base64.b64encode(
        f'{input_file}-{time.time_ns()}'.encode()
    ).decode()
    output_file = f'{unique_name}.geojson'
    output_path = os.path.join(current_app.config['UPLOAD_FOLDER'], output_file)

    get_statistic(input_file, data.indicator, data.start_date, data.end_date, output_path)
    output_file_url = url_for('auth.download_file', name=output_file)

    return {
        'url': output_file_url
    }, 200

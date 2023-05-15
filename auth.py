import os

from flask import Blueprint, request, jsonify, current_app, url_for, send_from_directory
from flask_login import login_user, login_required, current_user, logout_user
from werkzeug.utils import secure_filename

from webservice import db
from webservice.gee import get_statistic
from webservice.schemes import user_schema, projects_schema, projects_read_schema, project_read_schema
from webservice.models import Users, Projects, UsersProjects
from webservice.local import PLACEHOLDER_IMAGE

from werkzeug.security import check_password_hash

from datetime import datetime

import geopandas as gpd
import base64
import time
import hashlib

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


@auth.route('/project/', methods=['POST'])
@login_required
def new_project():
    data = {}

    # (filed_name, alias_for_msg)
    required_fields = [
        ('name', 'name'),
    ]

    for k, v in request.form.items():
        if k.startswith('user'):
            data.setdefault('users', []).append(v)
        else:
            data[k] = v

    data['thumbnail'] = request.files.get('thumbnail')

    for field in required_fields:
        if not data.get(field[0]):
            return {"detail": f'{field[1]} is required'}, 400

    file = data['thumbnail']
    if file:
        filename = secure_filename(file.filename)
        if filename:
            name, ext = os.path.splitext(filename)
            name = hashlib.sha1(name.encode()).hexdigext()
            filename = f'{name}{ext}'
            file.save(os.path.join(current_app.config['UPLOAD_FOLDER'], filename))
            data['thumbnail'] = url_for('auth.download_file', name=filename)
        else:
            data['thumbnail'] = url_for('auth.download_file', name=PLACEHOLDER_IMAGE)

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
    return projects_read_schema.jsonify(projects), 200


@auth.route('/api/projects/<project_id>/', methods=['GET'])
@login_required
def fetch_project(project_id):
    project = db.session.query(Projects).join(UsersProjects) \
         .filter(UsersProjects.user_id == current_user.id, UsersProjects.project_id == project_id).first()
    return project_read_schema.jsonify(project), 200


@auth.route('/api/projects/<project_id>/', methods=['DELETE'])
@login_required
def delete_project(project_id):
    project = db.session.query(Projects).join(UsersProjects) \
         .filter(UsersProjects.user_id == current_user.id, UsersProjects.project_id == project_id).first()
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


@auth.route('/query/', methods=['POST'])
@login_required
def query():
    data = {}

    # (filed_name, alias_for_msg)
    required_fields = [
        ('geo_data_file', 'Geo Data File'),
        ('start_date', 'Start Date'),
        ('end_date', 'End Date'),
        ('indicator', 'Indicator'),
    ]

    for k, v in request.form.items():
        data[k] = v

    data['geo_data_file'] = request.files.get('geo_data_file')

    for field in required_fields:
        if not data.get(field[0]):
            return {"detail": f'{field[1]} is required'}, 400

    file = data['geo_data_file']
    name, ext = os.path.splitext(
        secure_filename(file.filename)
    )
    unique_input_filename = hashlib.sha1(name.encode()).hexdigext()
    filename = f'{unique_input_filename}{ext}'
    input_file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)

    file.save(input_file_path)

    data['geo_data_file'] = url_for('auth.download_file', name=filename)

    db.session.query(Projects).filter(Projects.id == data['pid']).update({
        'query_start_date': data['query_start_date'],
        'query_end_date': data['query_end_date'],
        'query_indicator_id': data['query_indicator_id'],
    })
    db.session.commit()

    unique_output_filename = f'{unique_input_filename}-{time.time_ns()}'
    output_file = f'{unique_output_filename}.geojson'
    output_file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], output_file)

    get_statistic(input_file_path, data['indicator'], data['start_date'], data['end_date'], output_file_path)

    output_file_url = url_for('auth.download_file', name=output_file)

    db.session.query(Projects).filter(Projects.id == data['pid']).update({
        'query_report_url': output_file_url,
        'state': 1
    })
    db.session.commit()

    return {
        'url': output_file_url
    }, 200

from flask_login import UserMixin
from sqlalchemy_utils import URLType
from webservice import db

from datetime import datetime


class UsersProjects(db.Model):
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), primary_key=True)
    is_owner = db.Column(db.Boolean)


class Users(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(255))
    name = db.Column(db.String(30))
    created_at = db.Column(db.DateTime, default=datetime.now)
    logged_out = db.Column(db.Boolean)
    last_login = db.Column(db.DateTime)
    users_projects = db.relationship('UsersProjects', backref="user", cascade='all,delete')

    def __init__(self, email, password, name):
        self.email = email
        self.password = password
        self.name = name


class Projects(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30))
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.now)
    thumbnail = db.Column(URLType)
    geo_data_file = db.Column(URLType)
    users_projects = db.relationship('UsersProjects', backref="project", cascade='all,delete')
    country_id = db.Column(db.Integer, db.ForeignKey('countries.id'))
    query_report_url = db.Column(URLType)
    query_start_date = db.Column(db.DateTime)
    query_end_date = db.Column(db.DateTime)
    query_indicator_id = db.Column(db.Integer, db.ForeignKey('indicators.id'))
    state = db.Column(db.Integer, default=0)    # -1: Failed, 0: Pending, 1: Done


class Indicators(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.SmallInteger)
    name = db.Column(db.String(30))

    def __init__(self, indicator_type, name):
        self.type = indicator_type
        self.name = name


class Countries(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(5), unique=True)
    name = db.Column(db.String(50))

    def __init__(self, code, name):
        self.code = code
        self.name = name


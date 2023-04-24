from flask_login import UserMixin
from sqlalchemy_utils import URLType
from webservice import db

from datetime import datetime


user_projects = db.Table(
    'user_projects',
    db.Column('user_id', db.Integer, db.ForeignKey('users.id'), primary_key=True),
    db.Column('project_id', db.Integer, db.ForeignKey('projects.id'), primary_key=True),
    db.Column('is_owner', db.Boolean)
)


class Users(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(255))
    name = db.Column(db.String(30))
    created_at = db.Column(db.DateTime, default=datetime.now)
    logged_out = db.Column(db.Boolean)
    last_login = db.Column(db.DateTime)

    projects = db.relationship(
        'Projects',
        secondary=user_projects,
        lazy='subquery',
        backref=db.backref('users', lazy=True)
    )

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


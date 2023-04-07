from flask import Flask
from flask.cli import with_appcontext
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_login import LoginManager
from flask_cors import CORS

from werkzeug.security import generate_password_hash

from .local import SECRET_KEY, SQLALCHEMY_URI

from datetime import timedelta

import click

db = SQLAlchemy()
ma = Marshmallow()
lm = LoginManager()


def create_app():
    app = Flask(__name__, static_url_path='/static', static_folder='static')

    app.config['SECRET_KEY'] = SECRET_KEY
    app.config['SQLALCHEMY_DATABASE_URI'] = SQLALCHEMY_URI
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SESSION_PERMANENT'] = True
    app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=1)
    app.config['CORS_HEADERS'] = 'Content-Type'

    db.init_app(app)
    ma.init_app(app)
    lm.init_app(app)
   
    CORS(app, resources={r"/*": {"origins": "*"}})

    with app.app_context():
        from .models import Users, Indicators, Countries
        db.create_all()

        @lm.user_loader
        def load_user(user_id):
            return Users.query.get(int(user_id))

    # blueprint for auth routes in our app
    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint)

    # blueprint for non-auth parts of app
    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    @click.command(name='create_user')
    @click.option('--name')
    @click.option('--email')
    @click.option('--password')
    @with_appcontext
    def create_user(**arguments):
        arguments['password'] = generate_password_hash(arguments['password'], method='sha256')
        user = Users(**arguments)
        db.session.add(user)
        db.session.commit()

    @click.command(name='add_indicator')
    @click.option('--name')
    @click.option('--type')
    @with_appcontext
    def add_indicator(**arguments):
        indicator = Indicators(**arguments)
        db.session.add(indicator)
        db.session.commit()

    @click.command(name='add_country')
    @click.option('--name')
    @click.option('--code')
    @with_appcontext
    def add_country(**arguments):
        country = Countries(**arguments)
        db.session.add(country)
        db.session.commit()

    app.cli.add_command(create_user)
    app.cli.add_command(add_indicator)
    app.cli.add_command(add_country)

    return app

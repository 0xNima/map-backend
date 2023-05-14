from flask import Blueprint, request, jsonify, url_for
from webservice import db
from webservice.schemes import indicators_schema, countries_schema
from webservice.models import Indicators, Countries

import os

main = Blueprint('main', __name__)

STATIC_DIR = os.path.join(
    os.path.dirname(__file__), 'statics'
)


@main.route('/api/indicator/')
def indicator():
    indicators = Indicators.query.all()
    return indicators_schema.jsonify(indicators), 200


@main.route('/api/countries/')
def fetch_countries():
    countries = Countries.query.all()
    return countries_schema.jsonify(countries), 200

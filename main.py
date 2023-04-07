from flask import Blueprint, request, jsonify, url_for
from webservice import db
from webservice.schemes import indicators_schema, countries_schema
from webservice.models import Indicators, Countries

import os

main = Blueprint('main', __name__)

STATIC_DIR = os.path.join(
    os.path.dirname(__file__), 'static'
)


@main.route('/api/indicator/')
def indicator():
    indicators = Indicators.query.all()
    return indicators_schema.jsonify(indicators), 200


@main.route('/api/countries/')
def fetch_countries():
    countries = Countries.query.all()
    return countries_schema.jsonify(countries), 200


@main.route('/api/geo-data/', methods=['POST'])
def fetch_geodata():
    try:
        country = request.json['country']
        country_geodata_files = map(
            lambda file_name: url_for('static', filename=f'{country}/{file_name}'),
            filter(
                lambda file: os.path.splitext(file)[-1] == '.geojson',
                os.listdir(os.path.join(STATIC_DIR, country))
            )
        )
        return jsonify(list(country_geodata_files)), 200
    except FileNotFoundError:
        return jsonify({'detail': 'Country not found'}), 404

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
        country = request.json.get('country')
        if country:
            data = {}
            files = filter(
                lambda file: os.path.splitext(file)[-1] == '.geojson',
                os.listdir(os.path.join(STATIC_DIR, country))
            )

            for file in files:
                data.update({
                    os.path.splitext(file)[0]: url_for('static', filename=f'{country}/{file}')
                })

            return jsonify(data), 200
        return jsonify({'detail': 'Bad Data'}), 400
    except FileNotFoundError:
        return jsonify({'detail': 'Country not found'}), 404

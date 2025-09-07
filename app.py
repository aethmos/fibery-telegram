from flask import Flask, request, jsonify, send_file
import os
import json
import logging
import uuid
import requests
from datetime import datetime
from pathlib import Path

app = Flask(__name__)
logger = logging.getLogger('werkzeug')
logger.setLevel(logging.INFO)

BASE_DIR = Path(__file__).resolve().parent


def get_year_range(filter_obj):
	from_year = None
	to_year = None
	try:
		from_year = int(filter_obj.get('from')) if filter_obj and 'from' in filter_obj else None
	except Exception:
		from_year = None
	try:
		to_year = int(filter_obj.get('to')) if filter_obj and 'to' in filter_obj else None
	except Exception:
		to_year = None
	if from_year is None or isinstance(from_year, bool):
		from_year = datetime.utcnow().year - 1
	if to_year is None or isinstance(to_year, bool):
		to_year = datetime.utcnow().year
	years = []
	while from_year <= to_year:
		years.append(from_year)
		from_year += 1
	return years


@app.route('/logo', methods=['GET'])
def logo():
	logo_path = BASE_DIR / 'logo.svg'
	return send_file(str(logo_path))


@app.route('/', methods=['GET'])
def root():
	with open(BASE_DIR / 'config.app.json', 'r') as f:
		app_config = json.load(f)
	return jsonify(app_config)


@app.route('/validate', methods=['POST'])
def validate():
	return jsonify({'name': 'Public'})


@app.route('/api/v1/synchronizer/config', methods=['POST'])
def sync_config():
	with open(BASE_DIR / 'config.sync.json', 'r') as f:
		cfg = json.load(f)
	return jsonify(cfg)


@app.route('/api/v1/synchronizer/schema', methods=['POST'])
def schema():
	with open(BASE_DIR / 'schema.json', 'r') as f:
		schema_obj = json.load(f)
	return jsonify(schema_obj)


@app.route('/api/v1/synchronizer/datalist', methods=['POST'])
def datalist():
	resp = requests.get('https://date.nager.at/api/v3/AvailableCountries', timeout=30)
	resp.raise_for_status()
	countries = resp.json()
	items = [{'title': c['name'], 'value': c['countryCode']} for c in countries]
	return jsonify({'items': items})


@app.route('/api/v1/synchronizer/data', methods=['POST'])
def data():
	body = request.get_json(silent=True) or {}
	requested_type = body.get('requestedType')
	filter_obj = body.get('filter') or {}
	if requested_type != 'holiday':
		raise Exception('Only holidays database can be synchronized')
	countries = filter_obj.get('countries') or []
	if not countries:
		raise Exception('Countries filter should be specified')
	year_range = get_year_range(filter_obj)
	items = []
	for country in countries:
		for year in year_range:
			url = f'https://date.nager.at/api/v3/PublicHolidays/{year}/{country}'
			resp = requests.get(url, timeout=60)
			resp.raise_for_status()
			for item in resp.json():
				# Create stable UUID based on item content
				stable_id = uuid.uuid5(uuid.NAMESPACE_URL, json.dumps(item, sort_keys=True))
				item['id'] = str(stable_id)
				items.append(item)
	return jsonify({'items': items})


@app.errorhandler(404)
def not_found(e):
	return jsonify({'message': 'Not found', 'code': 404}), 404


@app.errorhandler(Exception)
def handle_exception(e):
	code = getattr(e, 'code', 500)
	message = str(e) if str(e) else 'Something goes wrong...'
	return jsonify({'message': message, 'code': code}), code


if __name__ == '__main__':
	port = int(os.environ.get('PORT', '8080'))
	app.run(host='0.0.0.0', port=port) 
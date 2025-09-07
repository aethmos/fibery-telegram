from datetime import datetime

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

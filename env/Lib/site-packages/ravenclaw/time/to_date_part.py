
from slytherin import remove_non_alphanumeric
from chronometry import to_date_part as lp_to_date_part
from chronometry import yearmonth_to_date as lp_yearmonth_to_date
from pandas import to_datetime




def to_day(date):
	try:
		return to_datetime(date).dt.day
	except:
		return lp_to_date_part(date=date, date_part='day')


def to_month(date):
	try:
		return to_datetime(date).dt.month
	except:
		return lp_to_date_part(date=date, date_part='month')

def to_quarter(date):
	try:
		return to_datetime(date).dt.quarter
	except:
		return lp_to_date_part(date=date, date_part='quarter')

def to_year(date):
	try:
		return to_datetime(date).dt.year
	except:
		return lp_to_date_part(date=date, date_part='year')

def to_yearmonth(date, sep ='-'):
	try:
		return date.map(lambda x: lp_to_date_part(date=x, date_part='year_month', sep=sep))
	except:
		return lp_to_date_part(date=date, date_part='yearmonth', sep = sep)

def to_yearquarter(date, sep ='-'):
	try:
		return date.map(lambda x: lp_to_date_part(date=x, date_part='year_quarter', sep=sep))
	except:
		return lp_to_date_part(date=date, date_part='yearquarter')

def to_monthname(date, abr = False):
	try:
		return date.map(lambda x: lp_to_date_part(date=x, date_part='month_name', abr=abr))
	except:
		return lp_to_date_part(date=date, date_part='month_name', abr=abr)

def to_weekdayname(date, abr = False):
	try:
		result = to_datetime(date).dt.weekday_name
		if abr:
			return result.str[:3]
		else:
			return result
	except:
		return lp_to_date_part(date=date, date_part='weekday_name', abr=abr)

def to_weekday(date):
	try:
		return date.map(lambda x: lp_to_date_part(date=x, date_part='weekday'))
	except:
		return lp_to_date_part(date=date, date_part='weekday')

def to_year_monthname(date, sep='-', abr=False):
	try:
		return date.map(lambda x: lp_to_date_part(date=x, date_part='year_monthname', sep=sep, abr=abr))
	except:
		return lp_to_date_part(date=date, date_part='year_monthname', sep=sep, abr=abr)

def yearmonth_to_date(x, day = 1):
	try:
		return x.map(lambda x: lp_yearmonth_to_date(x=x, day=day))
	except:
		return lp_yearmonth_to_date(x=x, day=day)

def to_date_part(date, date_part, sep='-', abr=False):
	date_part = date_part.lower()
	date_part = remove_non_alphanumeric(s=date_part, replace_with='', keep_underscore=False)

	if date_part == 'day':
		return to_day(date)
	elif date_part == 'month':
		return to_month(date)
	elif date_part == 'quarter':
		return to_quarter(date)
	elif date_part == 'yearmonth':
		return to_yearmonth(date=date, sep=sep)
	elif date_part == 'yearmonthname':
		return to_year_monthname(date=date, sep=sep, abr=abr)
	elif date_part == 'yearquarter':
		return to_yearquarter(date=date, sep=sep)
	elif date_part == 'monthname':
		return to_monthname(date = date, abr=abr)
	elif date_part == 'weekdayname':
		return to_weekdayname(date=date, abr=abr)
	elif date_part == 'weekday':
		return to_weekday(date=date)
	else:
		return to_year(date)
from pandas.core.series import Series

def replace_date_part(date, year = None, month = None, day = None):

	newdate = date.copy()
	if type(date) is Series:
		newdate = newdate.map(lambda x: x.replace(year = year, month = month, day = day))
	else:
		newdate = newdate.replace(year = year, month = month, day = day)

	return newdate

from chronometry import YearMonth

def as_yearmonth(x, sep='-', month_as='num'):
	try:
		return x.map(lambda x: YearMonth(x=x, sep=sep, month_as=month_as))
	except:
		return YearMonth(x=x, sep=sep, month_as=month_as)
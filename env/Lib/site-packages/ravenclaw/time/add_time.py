from chronometry import add_time as lp_add_time
from pandas.core.series import Series

def add_time(t, amount, unit ='day'):
	if type(t) is Series:
		return t.map(lambda x: lp_add_time(t = x, amount = amount, unit = unit))
	else:
		return lp_add_time(t = t, amount = amount, unit = unit)
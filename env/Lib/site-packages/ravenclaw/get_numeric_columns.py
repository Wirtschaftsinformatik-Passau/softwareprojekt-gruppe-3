from numpy import issubdtype, number
from pandas import Series, DataFrame, SparseDtype
from pandas.core.dtypes.dtypes import CategoricalDtype

def is_numeric(series):
	"""
	:type series: Series
	:rtype: bool
	"""
	try:
		return issubdtype(series.dtype, number)
	except TypeError as e:
		if isinstance(series.dtype, SparseDtype):
			return True
		elif isinstance(series.dtype, CategoricalDtype):
			return False
		else:
			print(series.dtype, type(series.dtype))
			raise e


def get_numeric_columns(data):
	"""
	:type data: DataFrame
	:rtype: list[str]
	"""
	return [column for column in data.columns if is_numeric(data[column])]


def get_non_numeric_columns(data):
	"""
	:type data: DataFrame
	:rtype: list[str]
	"""
	return [column for column in data.columns if not is_numeric(data[column])]


def fill_na_for_numeric(data, function=None, value=None, na_column_suffix=None):
	"""
	:type data: DataFrame
	:type na_column_suffix: NoneType or str
	:rtype: DataFrame
	"""
	if function is None and value is None:
		raise ValueError('either function or value should be provided')
	elif function is not None and value is not None:
		raise ValueError('either function or value should be None')

	data = data.copy()
	for column in get_numeric_columns(data=data):
		series = data[column]
		is_na = series.isna()
		if na_column_suffix and is_na.sum() > 0:
			data[column + na_column_suffix] = is_na.astype(int).values
		data[column] = series.fillna(value or function(series[series.notna()]))

	return data

from pandas import DataFrame


def get_difference(data1, data2):
	"""
	shows the difference between the two dataframes
	:type data1: DataFrame
	:type data2: DataFrame
	:rtype: DataFrame
	"""
	difference = (data1 != data2) & ((data1 == data1) & (data2 == data2))
	# the second (after or) part makes true cells for cells that are NaN in both dataframes

	d1 = data1[difference.any(axis='columns')]
	d2 = data2[difference.any(axis='columns')]

	result = DataFrame(index=d1.index)
	for col in difference.columns:
		if difference[col].any():
			result[f'{col}_1'] = d1[col]
			result[f'{col}_2'] = d2[col]

	return result

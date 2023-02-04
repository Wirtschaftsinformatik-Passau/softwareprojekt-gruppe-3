from .add_time import add_time

def construct_timeseries(data, time_col, group_by, value_cols = None, amounts = None, remove_duplicates = True, duplicate_to_keep='last', echo=True):
	if amounts is None:
		amounts = [{'unit':'day', 'numbers':[1]}]

	result = data.copy()
	merge_on_cols = group_by.copy()
	merge_on_cols.append(time_col)
	result.sort_values(by = merge_on_cols, inplace=True)

	duplicates = result.duplicated(subset=merge_on_cols)

	if duplicates.sum()>0:
		if remove_duplicates:
			result.drop_duplicates(subset=merge_on_cols, keep=duplicate_to_keep, inplace=True)
		else:
			print('Warning: there are duplicates in the data!')
			return None

	if echo: print('original shape:', data.shape)
	for amounts_dict in amounts:

		unit_plus = amounts_dict['unit']
		numbers = amounts_dict['numbers']
		if 'unit_alias' in amounts_dict:
			unit_alias = amounts_dict['unit_alias']
		else:
			if unit_plus in ['month', 'monthl', 'monthf']:
				unit_alias = 'month'
			else:
				unit_alias = unit_plus


		if unit_plus == 'monthl':
			unit = 'month'
			unit_suffix = ''
			keep = 'last' # of duplicates
		elif unit_plus == 'monthf':
			unit = 'month'
			unit_suffix = '_f'
			keep = 'first' # of duplicates
		elif unit_plus == 'month':
			unit = 'month'
			if duplicate_to_keep == 'last':
				unit_suffix = ''
			else:
				unit_suffix = '_f'
			keep = duplicate_to_keep
		else:
			unit = unit_plus
			unit_suffix = ''
			keep = duplicate_to_keep

		for number in numbers:

			if number!=0:

				if value_cols is None:
					timeshift_data = data.copy()
				else:
					only_columns = [time_col] + group_by + value_cols
					timeshift_data = data.copy()[only_columns]

				if unit=='number':
					timeshift_data[time_col] = timeshift_data[time_col] + number
				else:
					timeshift_data[time_col] = add_time(t=timeshift_data[time_col], amount=number, unit=unit)

				timeshift_data.drop_duplicates(subset=merge_on_cols, keep=keep, inplace=True)


				suffix = '_' + str(number) + (unit_alias if number==1 else unit_alias+'s') + '_' + ('earlier' if number>0 else 'later') + unit_suffix
				result = result.merge(right=timeshift_data, on=merge_on_cols, how='left', suffixes = ('', suffix))
	if echo: print('result shape:', result.shape)
	return result





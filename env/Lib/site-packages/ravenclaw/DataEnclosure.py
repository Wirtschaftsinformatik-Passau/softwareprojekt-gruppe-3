from slytherin.collections import has_duplicates

class DataEnclosure:
	def __init__(self, data, column_groups = None, row_groups = None):
		self._data = data
		data_columns = list(data.columns)
		if has_duplicates(list=data_columns):
			raise ValueError(f'there are duplicates in columns: {data_columns}')

		if column_groups is not None:
			for column_group, columns in column_groups.items():
				for column in columns:
					if column not in data_columns:
						raise KeyError(f'column "{column}" from group "{column_group}" does not exist in "{data_columns}"')

		self._col_groups = column_groups
		self._row_groups = row_groups

	@property
	def data(self):
		return self._data

	@property
	def columns(self):
		return list(self._data.columns)

	@property
	def rows(self):
		return list(self._data.index)

	@property
	def group_columns(self):
		return list(set([col for col_group in self._col_groups.values() for col in col_group]))

	def get_columns(self, column_group_names=None):
		if column_group_names is None:
			return self.columns
		else:
			columns = list(set([col for group in column_group_names for col in self._col_groups[group]]))
			columns_sorted = [col for col in self.columns if col in columns]
			return columns_sorted

	def get_rows(self, row_group_names=None):
		if row_group_names is None:
			return self.rows
		else:
			return list(set([row for group in row_group_names for row in self._row_groups[group]]))

	@property
	def other_columns(self):
		return [col for col in self.columns if col not in self.group_columns]

	def select(self, column_group_names = None, row_group_names = None):
		columns = self.get_columns(column_group_names=column_group_names)
		rows = self.get_rows(row_group_names=row_group_names)
		data = self.data.loc[rows, columns]
		if column_group_names is None:
			column_groups = self._col_groups
		else:
			column_groups = {group:self._col_groups[group] for group in column_group_names}

		if row_group_names is None:
			row_groups = self._row_groups
		else:
			row_groups = {group:self._row_groups[group] for group in row_group_names}

		return self.__class__(data=data, column_groups=column_groups, row_groups=row_groups)




from pandas import ExcelFile
from pandas import read_excel as pandas_read_excel
from collections import OrderedDict
from ..wrangling.standardize_columns import remove_non_alphanumeric_lower_and_join as standardize

def read_excel(io, all_sheets = False, sheets = None, standardize_columns = True, standardize_sheets = True, dtype = None, ignore_errors = False):

	if type(io) is not ExcelFile:
		excel_file = ExcelFile(io=io)
	else:
		excel_file = io

	if all_sheets:
		sheets = excel_file.book.sheet_names()

	result = OrderedDict()
	if sheets is None: sheets = [0]
	for sheet in sheets:
		if type(sheet) is int:
			sheet_name = excel_file.book.sheet_names()[sheet]
		else:
			sheet_name = str(sheet)

		num_rows = excel_file.book.sheet_by_name(sheet_name=sheet_name).nrows
		data_head = pandas_read_excel(io=excel_file, sheetname=sheet_name, skip_footer=num_rows, dtype=None)
		if standardize_columns:
			columns = [
				standardize(column, ignore_errors=ignore_errors) for column in data_head.columns
			]
			if type(dtype) is dict:
				dtype = dict(
					(standardize(key, ignore_errors=ignore_errors), value) for (key, value) in dtype.items()
				)
			data = pandas_read_excel(io=excel_file, sheetname=sheet_name, dtype=dtype, names = columns)
		else:
			data = pandas_read_excel(io=excel_file, sheetname=sheet_name, dtype=dtype)
		if len(sheets) == 1:
			return data

		if standardize_sheets: sheet_name = standardize(sheet_name, ignore_errors=ignore_errors)
		result[sheet_name] = data
	return result




import pandas as pd

def display(data, max_rows = None, max_cols = None):
	with pd.option_context('display.max_rows', max_rows, 'display.max_columns', max_cols):
		print(data)
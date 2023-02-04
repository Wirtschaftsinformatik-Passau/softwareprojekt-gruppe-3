from datetime import date
import pandas as pd
from .to_date_part import to_year, to_date_part

def get_calendar(year = None):
	if year is None:
		year = date.today().year
	first_day_of_the_year = date(year, 1, 1)
	calendar = pd.DataFrame({
		'date': pd.Series(pd.date_range(start = first_day_of_the_year, periods = 367)).dt.date
	})
	calendar.drop_duplicates(inplace = True)

	calendar = calendar[to_year(calendar.date)==year]
	calendar['year'] = year

	calendar['year_quarter'] = to_date_part(date=calendar.date, date_part='year_quarter')
	calendar['quarter'] = to_date_part(date=calendar.date, date_part='quarter')

	calendar['year_month'] = calendar['year_quarter'] = to_date_part(date=calendar.date, date_part='year_month')
	calendar['month'] = to_date_part(date=calendar.date, date_part='month')
	calendar['month_name'] = to_date_part(date=calendar.date, date_part='month_name')
	calendar['month_abr'] = to_date_part(date=calendar.date, date_part='month_name', abr=True)
	calendar['year_monthname'] = to_date_part(date=calendar.date, date_part='year_monthname', abr=True)

	calendar['weekday'] = to_date_part(date=calendar.date, date_part='weekday')
	calendar['weekday_name'] = to_date_part(date=calendar.date, date_part='weekday_name')
	calendar['weekday_abr'] = to_date_part(date=calendar.date, date_part='weekday_name', abr=True)
	calendar['day'] = to_date_part(date=calendar.date, date_part='day')

	return calendar
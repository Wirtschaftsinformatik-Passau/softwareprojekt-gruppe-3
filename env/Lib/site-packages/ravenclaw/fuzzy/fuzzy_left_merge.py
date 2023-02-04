from pandas import DataFrame, concat
from fuzzywuzzy import fuzz
from joblib import Parallel, delayed
from chronometry.progress import ProgressBar, iterate


def get_fuzz_ratio(s1, s2):
	return fuzz.ratio(s1, s2) / 100.0


def _get_similarity_between_two_strings(s1, s2, na_ratio, two_na_ratio, case_sensitivity, similarity_function):
	if similarity_function is None:
		similarity_function = get_fuzz_ratio

	if s1 is None and s2 is None:
		return two_na_ratio
	elif s1 is None or s2 is None:
		return na_ratio
	else:
		if case_sensitivity == 0:
			return similarity_function(s1.lower(), s2.lower())
		elif case_sensitivity == 1:
			return similarity_function(s1, s2)
		elif case_sensitivity > 1 or case_sensitivity < 0:
			raise ValueError('case_sensitivity should be between 0 and 1')
		else:
			cs_sim = similarity_function(s1, s2)
			ci_sim = similarity_function(s1.lower(), s2.lower())
			return cs_sim * case_sensitivity + ci_sim * (1 - case_sensitivity)


def _get_similarity_betweens_sets_of_strings(
		strings1, strings2, na_ratio, two_na_ratio, case_sensitivity, similarity_function,
		weights
):
	"""
	:type strings1: str or list[str] or tuple[str]
	:type strings2: str or list[str] or tuple[str]
	:type na_ratio: float
	:type two_na_ratio: float
	:rtype: float
	"""
	if not isinstance(strings1, (list, tuple, str)) or not isinstance(strings2, (list, tuple, str)):
		raise TypeError('strings1 and strings2 should be lists or tuples or strings')

	if isinstance(strings1, str):
		strings1 = [strings1]
	if isinstance(strings2, str):
		strings2 = [strings2]
	if weights is None:
		weights = [1] * len(strings1)

	if len(strings1) != len(strings2):
		raise ValueError('strings1 and strings2 should be of the same size')

	similarities = [
		_get_similarity_between_two_strings(
			s1=s1, s2=s2, na_ratio=na_ratio, two_na_ratio=two_na_ratio, case_sensitivity=case_sensitivity,
			similarity_function=similarity_function
		) * weight
		for s1, s2, weight in zip(strings1, strings2, weights)
	]
	return sum(similarities) / sum(weights)


def _get_similarity_between_strings_and_row(
		strings, row, right_on, na_ratio, two_na_ratio, case_sensitivity, similarity_function, weights
):
	return _get_similarity_betweens_sets_of_strings(
		strings1=strings, strings2=[row[x] for x in right_on], na_ratio=na_ratio, two_na_ratio=two_na_ratio,
		case_sensitivity=case_sensitivity, similarity_function=similarity_function, weights=weights
	)


def _find_best_matching_rows(
		strings, right, right_on, na_ratio, two_na_ratio, case_sensitivity, score_name, num_threads,
		similarity_function, weights, num_results, echo
):
	"""
	:param strings:
	:param right:
	:param right_on:
	:param na_ratio:
	:param two_na_ratio:
	:param case_sensitivity:
	:param score_name:
	:param num_threads:
	:param num_results:
	:param echo:
	:rtype: DataFrame
	"""
	right = right.copy()

	if num_threads == 1:

		right[score_name] = ProgressBar.apply(
			data=right,
			function=lambda row: _get_similarity_between_strings_and_row(
				strings=strings, row=row, right_on=right_on, na_ratio=na_ratio, two_na_ratio=two_na_ratio,
				case_sensitivity=case_sensitivity, similarity_function=similarity_function, weights=weights
			),
			echo=echo
		)

	else:

		parallel = Parallel(n_jobs=num_threads, backend='threading', require='sharedmem')
		progress_bar = ProgressBar(total=len(right) + 1, echo=echo)
		right[score_name] = parallel(
			delayed(_get_similarity_between_strings_and_row)(
				strings=strings, row=row, right_on=right_on, na_ratio=na_ratio, two_na_ratio=two_na_ratio,
				case_sensitivity=case_sensitivity, similarity_function=similarity_function, weights=weights
			)
			for index, row in iterate(right.iterrows(), progress_bar=progress_bar)
		)
		progress_bar.show(amount=len(right) + 1)

	right = right.sort_values(by=score_name, ascending=False)
	return right.iloc[0:num_results]


def _match_rows(
		row, right, left_on, right_on, na_ratio, two_na_ratio, score_name, case_sensitivity, num_results,
		similarity_function, num_threads, weights, echo
):
	"""
	:param row:
	:param right:
	:param left_on:
	:param right_on:
	:param na_ratio:
	:param two_na_ratio:
	:param score_name:
	:param case_sensitivity:
	:param num_results:
	:param num_threads:
	:param echo:
	:rtype: DataFrame
	"""
	strings = [row[x] for x in left_on]

	result = _find_best_matching_rows(
		strings=strings, right=right, right_on=right_on, na_ratio=na_ratio, two_na_ratio=two_na_ratio,
		case_sensitivity=case_sensitivity, score_name=score_name,
		num_results=num_results, similarity_function=similarity_function, weights=weights,
		num_threads=num_threads, echo=echo
	)
	result['fuzzy_id'] = row['fuzzy_id']
	result['match_rank'] = range(1, len(result) + 1)
	return result


def fuzzy_left_merge(
		left, right, left_on=None, right_on=None, on=None, suffixes=('_x', '_y'), score_name='match_ratio',
		na_ratio=0.5, two_na_ratio=0.75, similarity_function=None, weights=None,
		case_sensitivity=0.5, num_results=1, num_threads=-1, echo=1
):
	"""
	:type left: DataFrame
	:type right: DataFrame
	:type left_on: list[str] or str or NoneType
	:type right_on: list[str] or str or NoneType
	:type on: list[str] or str or NoneType
	:type how: str or NoneType
	:type case_sensitivity: float
	:type num_results: int
	:type similarity_function: callable
	:type echo: int or bool or ProgressBar
	:type num_threads: int
	:rtype: DataFrame
	"""
	if score_name in left.columns or score_name in right.columns:
		raise ValueError('use a score_name different from column names.')

	data1 = left.copy()
	data2 = right.copy()

	if on is None:
		on = data1.columns & data2.columns

	if left_on is None:
		left_on = on
	if right_on is None:
		right_on = on

	missing_left = [col for col in left_on if col not in data1.columns]
	if len(missing_left) > 0:
		raise KeyError(f'missing columns on left: {missing_left}')
	missing_right = [col for col in right_on if col not in data2.columns]
	if len(missing_right) > 0:
		raise KeyError(f'missing columns on right: {missing_right}')

	data1['fuzzy_id'] = range(len(data1))

	if num_threads == 1:
		results = ProgressBar.apply(
			data=data1,
			echo=echo,
			function=lambda row: _match_rows(
				row=row, right=data2, left_on=left_on, right_on=right_on, na_ratio=na_ratio, two_na_ratio=two_na_ratio,
				case_sensitivity=case_sensitivity, score_name=score_name, num_results=num_results,
				similarity_function=similarity_function, weights=weights,
				num_threads=1, echo=echo - 1
			)
		)

	else:
		parallel = Parallel(n_jobs=num_threads, backend='threading', require='sharedmem')
		progress_bar = ProgressBar(total=len(data1) + 1, echo=echo)

		results = parallel(
			delayed(_match_rows)(
				row=row, right=data2,
				left_on=left_on, right_on=right_on, na_ratio=na_ratio, two_na_ratio=two_na_ratio,
				case_sensitivity=case_sensitivity, score_name=score_name, num_results=num_results,
				similarity_function=similarity_function, weights=weights,
				num_threads=1, echo=echo - 1
			)
			for index, row in iterate(data1.iterrows(), progress_bar=progress_bar)
		)
		progress_bar.show(amount=len(data1) + 1)

	data2 = concat(results).reset_index(drop=True)

	return data1.merge(right=data2, on='fuzzy_id', how='left', suffixes=suffixes).drop(columns='fuzzy_id')

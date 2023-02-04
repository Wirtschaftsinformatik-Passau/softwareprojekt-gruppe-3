from ..get_sparql_dataframe import get_sparql_dataframe


def get_books(author="J. K. Rowling"):
	query = (
		"""
			SELECT ?book ?bookLabel ?authorLabel ?series_label (MIN(?publicationDate) AS ?publicationDate)
			WHERE
			{
		"""
		f'?author ?label "{author}"@en .'
		"""
			?book wdt:P31 wd:Q571 .
				?book wdt:P50 ?author .
				OPTIONAL {
					?book wdt:P179 ?series .
					?series rdfs:label ?series_label filter (lang(?series_label) = "en").
				}
				OPTIONAL {
					?book wdt:P577 ?publicationDate .
				}
				SERVICE wikibase:label {
					bd:serviceParam wikibase:language "en" .
				}
			}
			GROUP BY ?book ?bookLabel ?authorLabel ?series_label
			ORDER BY ?publicationDate
		"""
	)
	result = get_sparql_dataframe(service='https://query.wikidata.org/sparql', query=query)
	result.columns = ['id', 'label', 'author', 'series', 'publication_date']
	return result



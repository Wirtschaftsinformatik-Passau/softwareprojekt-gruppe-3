from ..get_sparql_dataframe import get_sparql_dataframe
from ...wrangling.split_rows import split_rows

# usage:
# from polarbear.data import wikidata as pbw
# x = pbw.get_companies()
def get_exchanges():
	query = (
		"""
			SELECT 
				?exchange ?exchangeLabel ?exchangeAltLabel 
				?countryLabel ?countryCode2Label ?countryCode3Label ?currencySymbol 
			WHERE {
				?exchange wdt:P31 wd:Q11691.
				OPTIONAL {
					?exchange wdt:P17 ?country.
					OPTIONAL { ?country wdt:P297 ?countryCode2. }
					OPTIONAL { ?country wdt:P298 ?countryCode3. }
				}
				OPTIONAL {
					?exchange wdt:P38 ?currency.
					?currency wdt:P498 ?currencySymbol.
				}
				SERVICE wikibase:label { bd:serviceParam wikibase:language "[AUTO_LANGUAGE],en". }
			}

		"""
	)
	result = get_sparql_dataframe(service='https://query.wikidata.org/sparql', query=query)
	result.columns = ['id', 'name', 'labels', 'country', 'country_code2', 'country_code3', 'currency']
	return result

def get_exchange_labels(exchanges = get_exchanges()):
	codes = split_rows(data=exchanges[['id', 'name', 'labels', 'country_code2']], by_column='labels', sep=',', keep_original=False)
	result = codes[['country_code2', 'id', 'name', 'labels']]
	result.columns = ['country_code2', 'id', 'name', 'label']
	return result


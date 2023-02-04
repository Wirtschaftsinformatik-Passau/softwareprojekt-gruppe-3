from ..get_sparql_dataframe import get_sparql_dataframe

# usage:
# from polarbear.data import wikidata as pbw
# x = pbw.get_companies()
def get_companies():
	query = (
		"""
			SELECT 
				?company 
				?companyLabel 
				?exchange
				?exchangeLabel 
				?tickerLabel 
			WHERE { 
				?company p:P414 [ ps:P414 ?exchange; pq:P249 ?ticker; ]. 
				SERVICE wikibase:label { 
					bd:serviceParam wikibase:language "[AUTO_LANGUAGE],en". 
				} 
			}

		"""
	)
	result = get_sparql_dataframe(service='https://query.wikidata.org/sparql', query=query)
	result.columns = ['id', 'company', 'exchange_id', 'exchange_name', 'ticker']
	return result
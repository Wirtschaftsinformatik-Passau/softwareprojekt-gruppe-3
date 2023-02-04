
from ..get_sparql_dataframe import get_sparql_dataframe

def get_countries():
	query = """
		SELECT 
			?country ?countryLabel ?population ?countryCode2 ?countryCode3 
			(AVG(?lat) AS ?latitude) (AVG(?long) AS ?longitude)
		WHERE
		{
			?country  wdt:P31 wd:Q6256 ;
				wdt:P1082 ?population ;
				wdt:P297 ?countryCode2 ;
				wdt:P298 ?countryCode3 ;
			p:P625 [
				psv:P625 [
					wikibase:geoLatitude ?lat ;
					wikibase:geoLongitude ?long ;
				]
			]
			
			SERVICE wikibase:label { bd:serviceParam wikibase:language "en" }
		}
		GROUP BY ?country ?countryLabel ?population ?countryCode2 ?countryCode3
	"""
	result = get_sparql_dataframe(service='https://query.wikidata.org/sparql', query=query)
	result.columns = ['id', 'country', 'population', 'code2', 'code3', 'latitude', 'longitude']
	return result

def get_cities():
	query = """
		SELECT ?city ?cityLabel ?population ?country ?countryLabel 
		(AVG(?lat) AS ?latitude) (AVG(?long) AS ?longitude)
		WHERE {
			?city wdt:P31/wdt:P279* wd:Q515 ;
				wdt:P1082 ?population ;
				wdt:P17 ?country ;
				p:P625 [
					psv:P625 [
						wikibase:geoLatitude ?lat;
						wikibase:geoLongitude ?long;
					]
				]
			SERVICE wikibase:label {
				bd:serviceParam wikibase:language "en" .
			}
		}
		GROUP BY ?city ?cityLabel ?population ?country ?countryLabel
	"""
	result = get_sparql_dataframe(service='https://query.wikidata.org/sparql', query=query)
	result.columns = ['id', 'city', 'population', 'country_id', 'country', 'latitude', 'longitude']
	return result
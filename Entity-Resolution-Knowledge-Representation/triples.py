from rdflib import Graph, URIRef, Literal, XSD, Namespace, RDF, RDFS
import json 

FOAF = Namespace('http://xmlns.com/foaf/0.1/')
MYNS = Namespace('http://inf558.org/myfakenamespace#')
SCHEMA = Namespace('http://schema.org/')

my_kg = Graph()

imdb_data = []
for line in open('imdb.jl', 'r'):
    imdb_data.append(json.loads(line))

afi_data = []
for line in open('afi.jl', 'r'):
    afi_data.append(json.loads(line))

matched_data = []
for line in open('matched.jl', 'r'):
    matched_data.append(json.loads(line))

my_kg.bind('myns', MYNS)
my_kg.bind('foaf', FOAF)
my_kg.bind('schema', SCHEMA)

data = []
for movie in matched_data:
	int_data = {}
	imdb_uri = movie['imdb_movie']
	int_data['imdb_uri'] = imdb_uri
	afi_uri = movie['afi_movie']
	int_data['afi_uri'] = afi_uri
	for x in imdb_data:
		for k,v in x.items():
			if v == imdb_uri:
				int_data['title'] = x.get('name',None) 
				int_data['release-date'] = x.get('year',None) 
				int_data['certificate'] = x.get('certificate',None)
				int_data['runtime'] = x.get('runtime',None) 
				int_data['genre'] = x.get('genre',None) 
				int_data['imdb-rating'] = x.get('rating',None) 
				int_data['imdb-metascore'] = x.get('metascore',None) 
				int_data['imdb-votes'] = x.get('votes',None) 
				int_data['gross-income'] = x.get('gross',None) 
	for y in afi_data:
		for k,v in y.items():
			if v == afi_uri:
				int_data['producer'] = y.get('producer',None) 
				int_data['writer'] = y.get('writer',None)
				int_data['cinematographer'] = y.get('cinematographer',None)
				int_data['production-company'] = y.get('production_company',None)
	data.append(int_data)

for movie in data:
	imdb_uri = movie['imdb_uri']
	node_uri = URIRef(imdb_uri)
	my_kg.add((node_uri, RDF.type, MYNS['Movie']))
	for k,v in movie.items():
		if k == 'title' and v != None:
			my_kg.add((node_uri, FOAF['title'], Literal(movie['title'])))
		if k == 'release-date' and v!= None :
			my_kg.add((node_uri, SCHEMA['datePublished'], Literal(movie['release-date'], datatype=XSD.date)))
		if k == 'certificate' and v!= None:
			my_kg.add((node_uri, MYNS['certificate'], Literal(movie['certificate'])))
		if k == 'runtime' and v!= None: 
			my_kg.add((node_uri, MYNS['runtime'], Literal(movie['runtime'])))
		if k == 'genre' and v!= None: 
			genres = movie['genre'].split(',')
			for m in genres:
				my_kg.add((node_uri, SCHEMA['genre'], Literal(m)))
		if k == 'imdb-rating' and v!= None :
			my_kg.add((node_uri, MYNS['imdb-rating'], Literal(movie['imdb-rating'], datatype=XSD.decimal)))
		if k == 'imdb-metascore' and v!= None: 
			my_kg.add((node_uri, MYNS['imdb-metascore'], Literal(movie['imdb-metascore'], datatype=XSD.integer)))
		if k == 'imdb-votes' and v!= None: 
			my_kg.add((node_uri, MYNS['imdb-votes'], Literal(movie['imdb-votes'], datatype=XSD.integer)))
		if k == 'gross-income' and v!= None:
			my_kg.add((node_uri, MYNS['gross-income'], Literal(movie['gross-income'])))
		try:
			if k == 'producer' and v!= None: 
				my_kg.add((node_uri, MYNS['producer'], Literal(movie['imdb-votes'])))
			if k == 'writer' and v!= None: 
				my_kg.add((node_uri, MYNS['writer'], Literal(movie['writer'])))
			if k == 'cinematographer' and v!= None: 
				my_kg.add((node_uri, MYNS['cinematographer'], Literal(movie['cinematographer'])))
			if k == 'imdb-votes' and v!= None: 
				my_kg.add((node_uri, MYNS['imdb-votes'], Literal(movie['imdb-votes'], datatype=XSD.integer)))
			if k == 'production-company' and v!= None: 
				prod = movie['production-company'].replace(" ", "")
				prodcom_uri = URIRef(prod)
				my_kg.add((prodcom_uri, RDF.type, SCHEMA['Organization']))
				my_kg.add((prodcom_uri, RDFS.label, Literal(movie['production-company'])))
				my_kg.add((node_uri, SCHEMA['productionCompany'], prodcom_uri))
		except:
			continue

my_kg.serialize('Divya_Suri_hw03_movie_triples.ttl', format="turtle")
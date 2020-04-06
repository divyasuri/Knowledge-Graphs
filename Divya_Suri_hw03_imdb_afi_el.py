import rltk 
import json 
import re

class IMDBRecord(rltk.Record):
	def __init__(self, raw_object):
		super().__init__(raw_object)
		self.name = ''

	@rltk.cached_property
	def id(self):
		return self.raw_object['url']

	@rltk.cached_property
	def name_string(self):
		return self.raw_object['name']

	@rltk.cached_property
	def year(self):
		return str(self.raw_object['year'])

	@rltk.cached_property
	def genre_set(self):
		return set(self.raw_object['genre'].split(','))

class AFIRecord(rltk.Record):
	def __init__(self, raw_object):
		super().__init__(raw_object)
		self.name = ''

	@rltk.cached_property
	def id(self):
		return self.raw_object['url']

	@rltk.cached_property
	def name_string(self):
		return self.raw_object['title']

	@rltk.cached_property
	def date_string(self):
		return self.raw_object.get('release_date', '')

	@rltk.cached_property
	def genre_string(self):
		return self.raw_object.get('genre','')

	@rltk.cached_property
	def genre_set(self):
		return set(self.genre_string.split(','))

	@rltk.cached_property
	def year(self):
		if re.search("(\d{4})",self.date_string):
			return str(re.search("(\d{4})",self.date_string).group(0))
		else:
			return ''

imdb_file = 'imdb.jl'
afi_file  = 'afi.jl'

ds_imdb = rltk.Dataset(reader=rltk.JsonLinesReader(imdb_file), record_class=IMDBRecord, adapter=rltk.MemoryKeyValueAdapter())
ds_afi  = rltk.Dataset(reader=rltk.JsonLinesReader(afi_file),  record_class=AFIRecord,  adapter=rltk.MemoryKeyValueAdapter())

def name_similarity(r_imdb, r_afi):
	s1 = r_imdb.name_string
	s2 = r_afi.name_string
	return rltk.jaro_winkler_similarity(s1, s2)

def genre_similarity(r_imdb, r_afi):
	s1 = r_imdb.genre_set
	s2 = r_afi.genre_set
	return rltk.jaccard_index_similarity(s1, s2)

def year_similarity(r_imdb, r_afi):
	s1 = r_imdb.year
	s2 = r_afi.year
	if s1 == s2:
		return 1
	else:
		return 0 

def rule_based_method(r_imdb, r_afi):
	threshold = 0.7
	name_score = name_similarity(r_imdb, r_afi)
	genre_score = genre_similarity(r_imdb, r_afi)
	year_score = year_similarity(r_imdb,r_afi)
	total = 0.7 * name_score + 0.1 * genre_score + 0.2 * year_score 
	return total > threshold,total

matches = {}
candidate_pairs = rltk.get_record_pairs(ds_imdb, ds_afi)
for r_imdb, r_afi in candidate_pairs:
	result, confidence = rule_based_method(r_imdb, r_afi)
	if result == True:
		matches[r_imdb.id] = r_afi.id 

imdb_text = []
for line in open('imdb.jl', 'r'):
	imdb_text.append(json.loads(line))

data = []
for record in imdb_text:
	rec = {}
	url = record['url']
	if url in matches:
		rec['imdb_movie'] = url
		rec['afi_movie'] = matches[url]
		data.append(rec)
	else:
		rec['imdb_movie'] = url
		rec['afi_movie'] = None 
		data.append(rec)

with open('Divya_Suri_hw03_imdb_afi_el.json', 'w', encoding='utf-8') as f:
	json.dump(data, f, ensure_ascii=False, indent = 2)

#!/usr/bin/env python
# coding: utf-8

# import libraries and define functions.

import pandas
import pathlib
import pydash
import requests
import unidecode

def value_extract(row, col):

    # extract dictionary values.

    return pydash.get(row[col], 'value')

def sparql_query(query, service):

    # send sparql request, and formulate results into a dataframe.

    r = requests.get(service, params = {'format': 'json', 'query': query})
    data = pydash.get(r.json(), 'results.bindings')
    data = pandas.DataFrame.from_dict(data)
    for x in data.columns:
        data[x] = data.apply(value_extract, col=x, axis=1)
    return data

def string_norm(row, col):

    # normalise strings for matching.

    if row[col]:
        return unidecode.unidecode(str(row[col])).upper()

def annual_query(filt):

    # capture year period of wikidata film/creator data
    # or all films without publication date.
    
    annual = sparql_query("""
        SELECT DISTINCT ?creator ?creatorLabel ?work  ?workLabel ?title 
        WHERE {
            ?work wdt:P31 wd:Q11424.
            """+filt+"""
            ?work ?property ?creator.
            OPTIONAL { ?work wdt:P1476 ?title. }.
            ?creator wdt:P31 wd:Q5.
            SERVICE wikibase:label { bd:serviceParam wikibase:language "en". }
        }""", 'https://query.wikidata.org/sparql')

    if len(annual):

        annual = pandas.concat([
            annual.copy().rename(columns={'workLabel':'work_name'}),
            annual.copy().rename(columns={'title':'work_name'})])

        annual = annual.rename(columns={
                'creator':'creator_id',
                'creatorLabel':'creator_name',
                'work':'work_id'})

        for x in ['creator_id', 'work_id']:
            annual[x] = annual[x].str.split('/').str[-1]

        for x in ['creator_name', 'work_name']:
            annual[x] = annual.apply(string_norm, col=x, axis=1)

        annual = annual[['creator_id', 'creator_name', 'work_id', 'work_name']]
        annual = annual.loc[annual.work_id != annual.work_name]
        annual = annual.drop_duplicates().dropna()

        return annual

# build dataframe of wikidata film titles and creators.

query_filter = """FILTER NOT EXISTS { ?work wdt:P577 [] }."""
dataframe = annual_query(query_filter)

for year in range(1890, 2030):
    query_filter = """
        ?work wdt:P577 ?publication.
        FILTER(YEAR(?publication) >= """+str(year)+""").
        FILTER(YEAR(?publication) < """+str(year+1)+""").
        """
    dataframe = pandas.concat([dataframe, annual_query(query_filter)])

save_path = pathlib.Path.home() / 'wikidata-data.csv'
dataframe.to_csv(save_path, index=False)
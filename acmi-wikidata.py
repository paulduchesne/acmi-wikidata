#!/usr/bin/env python3
# coding: utf-8

# load libraries.

import json
import pandas
import pathlib
import pydash
import unidecode
import requests
import sys

# load filmography repo code as a module.
sys.path.extend(['/home/paulduchesne/git/filmography-matching'])
import filmographymatching

# define functions.

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

def parse_single(row, col, val):

    # extract single dictionary values.

    return pydash.get(row[col], val) 

# pathways for csvs.

acmi_path = pathlib.Path.home() / 'acmi-data.csv'
wikidata_path = pathlib.Path.home() / 'wikidata-data.csv'
result_path = pathlib.Path.cwd() / 'results.csv'

# parse ACMI API to dataframe.

if not acmi_path.exists():
    api_path = pathlib.Path.home() / 'git' / 'acmi-api' / 'app' / 'json' / 'works'
    api_data = [x for x in api_path.rglob('**/*') if x.suffix == '.json']

    cols = ['acmi_id', 'id', 'title', 'creators_primary']
    dataframe = pandas.DataFrame(columns=cols)

    for n, x in enumerate(api_data):
        with open(x, encoding='utf-8') as a:
            a = json.load(a)
            if pydash.get(a, 'type') == 'Film':
                dataframe.loc[len(dataframe)] = [pydash.get(a, c) for c in cols]

    dataframe = dataframe.rename(columns={'id': 'work_id', 'title': 'work_name'})
    dataframe = dataframe.explode('creators_primary')
    dataframe['creator_name'] = dataframe.apply(parse_single, col='creators_primary', val='name', axis=1)
    dataframe['creator_id'] = dataframe.apply(parse_single, col='creators_primary', val='creator_id', axis=1)

    dataframe = dataframe.dropna(subset=['creator_id'])
    dataframe = dataframe.copy()
    dataframe['creator_id'] = dataframe['creator_id'].astype(int)
    dataframe = dataframe[['creator_id', 'creator_name', 'work_id', 'work_name']]

    dataframe['work_name'] = dataframe['work_name'].str.split(' = ').str[0].str.strip()
    for x in ['work_name', 'creator_name']:
        dataframe[x] = dataframe.apply(string_norm, col=x, axis=1)

    # reduction to sample set not required for proper run.  

    sample = ['00021685', '00022021', '00023211', '00023583', '00024730', '00026128', '00030241', 
        '00030804', '00035050', '00035746', '00036317', '00067909', '00071762', '00076133', 
        '00076873', '00077807', '00078215', '00080241', '00082218', '00082981']
    dataframe = dataframe.loc[dataframe.creator_id.isin([int(x) for x in sample])]

    dataframe = dataframe.loc[~dataframe.creator_name.isin([''])]
    dataframe.to_csv(acmi_path, index=False)

# parse Wikidata data to dataframe.

if not wikidata_path.exists():
    query_filter = """FILTER NOT EXISTS { ?work wdt:P577 [] }."""
    dataframe = annual_query(query_filter)

    for year in range(1890, 2030):
        query_filter = """
            ?work wdt:P577 ?publication.
            FILTER(YEAR(?publication) >= """+str(year)+""").
            FILTER(YEAR(?publication) < """+str(year+1)+""").
            """
        dataframe = pandas.concat([dataframe, annual_query(query_filter)])

    dataframe.to_csv(wikidata_path, index=False)

# run filmographymatching process.

if not result_path.exists():
    filmographymatching.match(acmi_path, wikidata_path, result_path)

print('all done.')

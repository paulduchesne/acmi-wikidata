#!/usr/bin/env python
# coding: utf-8

# import libraries and define functions.

import json
import pandas
import pathlib
import pydash
import unidecode

def parse_single(row, col, val):

    # extract single dictionary values.

    return pydash.get(row[col], val) 

def string_norm(row, col):

    # normalise strings for matching.

    return unidecode.unidecode(row[col]).upper()

# convert acmi json files to normalised dataframe.

api_path = pathlib.Path.home() / 'acmi-api' / 'app' / 'json' / 'works'
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

dataframe = dataframe.loc[~dataframe.creator_name.isin([''])]
save_path = pathlib.Path.home() / 'acmi-data.csv'
dataframe.to_csv(save_path, index=False)
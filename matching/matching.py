#!/usr/bin/env python
# coding: utf-8

# load libraries.

import datetime
import pandas
import pathlib
from thefuzz import process
from thefuzz import fuzz

# load acmi data.

acmi_path = pathlib.Path.home() / 'acmi-data.csv'
acmi_data = pandas.read_csv(acmi_path)
print('acmi data', len(acmi_data))

# load wikidata data.

wikidata_path = pathlib.Path.home() / 'wikidata-data.csv'
wikidata_data = pandas.read_csv(wikidata_path)
print('wikidata data', len(wikidata_data))

# find matching filmographies for each acmi creator. 

acmi_creator_list = list(acmi_data.creator_id.unique())
commence = datetime.datetime.now()
for i, x in enumerate(acmi_creator_list):
    save_path = pathlib.Path.cwd() / 'data' / f'{str(x).zfill(8)}.csv'
    save_path.parents[0].mkdir(exist_ok=True)
    if not save_path.exists():

        # progress report
        t = (datetime.datetime.now()-commence)/(i+1)
        time_to_finish = (((t)*(len(acmi_creator_list)))+commence).strftime("%Y-%m-%d %H:%M:%S")
        print(f'processing: {i+1} of {len(acmi_creator_list)}; eta {time_to_finish}.')

        # grab creator name.
        acmi_name = acmi_data.copy()
        acmi_name = acmi_name.loc[acmi_name.creator_id.isin([x])].iloc[0]['creator_name']

        # limit to acmi creator data.
        acmi_titles = acmi_data.copy()
        acmi_titles = acmi_titles.loc[acmi_titles.creator_id.isin([x])]

        # find all possible wikidata candidates for matching.
        wikidata_creator_names = [str(x) for x in wikidata_data.creator_name.unique()]
        candidates = process.extract(str(acmi_name), wikidata_creator_names,
            limit=1000, scorer=fuzz.token_sort_ratio)
        candidates = [x[0] for x in candidates if x[1] > 70]

        # limit to candidate wikidata data.
        wikidata_candidate = wikidata_data.copy()
        wikidata_candidate = wikidata_candidate.loc[wikidata_candidate.creator_name.isin(candidates)]

        # define dataframe for results table.
        col = ['acmi_id', 'acmi_name',
            'wikidata_id', 'wikidata_name',
            'acmi_title', 'wikidata_title', 'match']
        result_dataframe = pandas.DataFrame(columns=col)

        # loop through possible candidates.
        for y in wikidata_candidate.creator_id.unique():
            wikidata_name = wikidata_data.copy()
            wikidata_name = wikidata_name.loc[wikidata_name.creator_id.isin([y])]
            wikidata_name = wikidata_name.iloc[0]['creator_name']

            # candidate filmography.
            wikidata_titles = wikidata_data.copy()
            wikidata_titles = wikidata_titles.loc[wikidata_titles.creator_id.isin([y])]

            # find best title match from candidate filmography for each film of acmi creator.
            match_list = list()
            for z in acmi_titles.work_name.unique():
                match = process.extractOne(z, list(wikidata_titles.work_name.unique()),
                    scorer=fuzz.token_sort_ratio)
                match_list.append(match[1])
                result_dataframe.loc[len(result_dataframe)] = [str(x), str(acmi_name),
                    str(y), str(wikidata_name), str(z), str(match[0]), str(match[1])]

        # write results for further processing.
        result_dataframe.to_csv(save_path, index=False)

print('all done.')

# ACMI // Wikidata
Entity matching between ACMI and Wikidata.

This repository is part of an ongoing experiment in matching entities between different sets of filmographic data, in this case collection data from the Australian Centre for the Moving Image via their [public API](https://github.com/ACMILabs/acmi-api) and data drawn from [Wikidata](https://www.wikidata.org/).

## ACMI data

ACMI data is produced by parsing JSON from the [public API repository](https://github.com/ACMILabs/acmi-api) into a single table with columns for entity id, entity name, work id and work name. Note that the resulting data is filtered to only those records with the "type" of "Film".

## Wikidata data

Wikidata data is produced in response to a SPARQL query, requesting all "creators" (note that this currently is defined as [human](https://www.wikidata.org/wiki/Q5)) with some form of interaction with a [film](https://www.wikidata.org/wiki/Q11424). This query is currently lacking in nuance, so does not include creator organisations (eg production companies) and will also return individuals not directly related to the production of the film (eg "based on a book by"). The query itself is also too intensive to be submitted once, so is broken down by production year (with an additional query for films which do not contain this data).

## Matching

The method used here is based on suggestions made by Georg Eckes (Bundesarchiv, Berlin) in 2019 during a discussion around practical linked open data strategies for film archives, and possible linking methodologies.

This process follows these steps:
- select a specific subject to be matched from dataset A.
- assemble a list of film titles from dataset A attributed to that subject.
- gather a list of possible candidates from dataset B based on very loose name matching.
- assemble lists of film titles from dataset B for each candidate. 
- for each candidate, for each title in the first list, find the highest matching title match from the candidate film list.
- score each candidate by the median score for each title match.
- currently a pass is awarded for a median of 100, and is accepted if only one candidate achieves this score.

## Matching example

The following is an actual example of how this functions, using ACMI ID 34373 AGNES VARDA as a test case.
ACMI lists five works against this entity: [LES CREATURES, JACQUOT DE NANTES [WIDESCREEN], THE GLEANERS AND I, CLEO FROM 5 TO 7, VAGABOND].
Extremely loose string matching return 440 possible entity matches from Wikidata - we will focus on two: [Václav Hanuš (Q94909886)](https://www.wikidata.org/wiki/Q94909886) and [Agnès Varda (Q229990)](https://www.wikidata.org/wiki/Q229990). For each of these candidates, we return a filmography list from Wikidata.

## Further matching

## Known issues

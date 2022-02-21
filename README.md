# ACMI // Wikidata
Entity matching between ACMI and Wikidata.

This repository is part of an ongoing experiment in matching entities between different sets of filmographic data, in this case collection data from the Australian Centre for the Moving Image via their [public API](https://github.com/ACMILabs/acmi-api) and data drawn from [Wikidata](https://www.wikidata.org/).

## ACMI data

ACMI data is produced by parsing JSON from the [public API repository](https://github.com/ACMILabs/acmi-api) into a single table with columns for entity id, entity name, work id and work name. Note that the resulting data is filtered to only those records with the "type" of "Film".

## Wikidata data

Wikidata data is produced in response to a SPARQL query, requesting all "creators" (note that this currently is defined as [human](https://www.wikidata.org/wiki/Q5)) with some form of interaction with a [film](https://www.wikidata.org/wiki/Q11424). This query is currently lacking in nuance, so does not include creator organisations (eg production companies) and will also return individuals not directly related to the production of the film (eg "based on a book by"). The query itself is also too intensive to be submitted once, so is broken down by production year (with an additional query for films which do not contain this data).

## Matching

The matching process uses the [filmography matching](https://github.com/paulduchesne/filmography-matching) module. A detailed description of the process can be found there.

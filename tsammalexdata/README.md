The tsammalexdata package
-------------------------

The ``tsammalexdata`` package provides the following functionality:

- A test suite which can be invoked by travis-ci (or locally) to check integrity of the data.
- Scripts to enrich the core data with supplemental data from external sources (like EOL of GBIF).


Making a release of the data:

1. Run the tests
2. Harvest additional data:
```bash
    python eol.py
    python gbif.py
    ~/venvs/gis/bin/python ecoregion_from_occurrence.py
```

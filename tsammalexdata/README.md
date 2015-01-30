The tsammalexdata package
-------------------------

The ``tsammalexdata`` package provides the following functionality:

- A test suite which can be invoked by travis-ci (or locally) to check integrity of the data.
- Scripts to enrich the core data with supplemental data from external sources (like EOL of GBIF).


Making a release of the data:

1. Make sure the tests pass:
```
    $ nosetests
    ----------------------------------------
    Ran ...

    OK
```
2. Harvest additional data and compute distribution data:
```bash
    python species.py
    ~/venvs/gis/bin/python distribution.py
```
3. Upload images.

The tsammalexdata package
-------------------------

Making a release of the data:

1. Run the tests
2. Harvest additional data:

    python eol.py
    python gbif.py
    ~/venvs/gis/bin/python ecoregion_from_occurrence.py

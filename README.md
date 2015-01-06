Tsammalex Data
==============

[![Build Status](https://travis-ci.org/clld/tsammalex-data.svg?branch=master)](https://travis-ci.org/clld/tsammalex-data)

This repository holds the data served by http://tsammalex.clld.org/
The data is licensed under a Creative Commons Attribution 4.0 International License.

The data is stored as collection of csv files, suitable for editing with LibreOffice.


Adding images
-------------

Adding an image is done in two steps:

1. Adding a row to ``images.csv``, specifying a publicly available URL to access the image in the ``source_url`` column (this may be a temporary GitHub repository, wikimedia commons or other publicly available webspace).
2. Providing the image at the specified URL for download.

When a data release is created, new images will be fetched from the sources and uploaded to [Edmond](http://edmond.mpdl.mpg.de/imeji/collection/d2JGQRxO19XTOEXG) - the MPS' media repository.


Referential Integrity
---------------------

Currently, insuring referential integrity of the data is the responsibility of the editor. In particular editors have
to make sure

- ``id`` columns hold unique values,
- ``<name>__id`` columns hold values which exist as ``id`` in the referenced table,
- ``<name>__ids`` columns hold comma-separated lists of values which exist as ``id`` in the referenced table.

Upon push, referential integrity will be checked by travis-ci.


Changing the scientific name of a species
-----------------------------------------

Since the ``id`` of a species is created from its scientifc name, changing this name involves the following steps:

1. Add a new species with the updated name and ``id`` to ``species.csv``.
2. Update all references to the ``id`` in ``images.csv`` and ``words.csv``.
3. **TODO** redirect the old species to the new one by ...


Supplemental Data
-----------------

In addition to the data managed in this repository, we fetch data from other sources to enhance the usability of the site.

- Given a proper scientific name for a species we can fetch a corresponding identifier from [EOL](http://eol.org).
- Given an EOL identifier, we can information about the biological classification of a species and a common english name.
- We also use information on terrestrial ecoregions from WWF, which can be referenced using ecoregion identifiers in the format ``AT0101``.
- WWF ecoregions and countries in which a species occurs can be computed by matching [occurrence information](http://www.gbif.org/occurrence) from [GBIF](http://www.gbif.org) against region borders.


Notes
-----

Notes to self:

- To diff sorted lines, you may run:

    diff -b <(sort words.csv) <(sort words_CN.csv)


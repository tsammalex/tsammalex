Tsammalex Data
==============

This repository holds the data served by http://tsammalex.clld.org/
The data is licensed under a Creative Commons Attribution 4.0 International License.


Workflow
--------

The data is stored as collection of csv files, suitable for editing with LibreOffice.


Adding images
~~~~~~~~~~~~~

Adding an image is done in two steps:

1. Adding a row to ``images.csv``, specifying a publicly available URL to access the image (this may be a temporary GitHub repository, or other publicly available webspace).
2. Providing the image at the specified URL for download.


Referential Integrity
---------------------

Currently, insuring referential integrity of the data is the responsibility of the editor. In particular editors have
to make sure

- ``id`` columns hold unique values,
- ``<name>__id`` columns hold values which exist as ``id`` in the referenced table,
- ``<name>__ids`` columns hold comma-separated lists of values which exist as ``id`` in the referenced table.

At some point we will need tools to check referential integrity on push - maybe implemented as travis-ci
job.


Supplemental Data
-----------------

In addition to the data managed in this repository, we fetch data from other sources to enhance the usability of the site.

- Given a proper scientific name for a species we can fetch a corresponding identifier from [EOL](http://eol.org).
- Given an EOL identifier, we can information about the biological classification of a species and a common english name.
- We also use information on terrestrial ecoregions from WWF, which can be referenced using ecoregion identifiers in the format ``AT0101``.


Notes
-----

Notes to self:

- To diff sorted lines, you may run:

    diff -b <(sort words.csv) <(sort words_CN.csv)


Tsammalex Data
==============

[![Build Status](https://travis-ci.org/clld/tsammalex-data.svg?branch=master)](https://travis-ci.org/clld/tsammalex-data)

This repository holds the data served by http://tsammalex.clld.org/
The data is licensed under a Creative Commons Attribution 4.0 International License.

The data is stored as collection of csv files, suitable for editing with LibreOffice.


Adding images
-------------

Adding an image is done in two steps:

1. Adding a row to ``staged_images.csv``, specifying a publicly available URL to access the image in the ``id`` column (this may be a temporary GitHub repository, wikimedia commons or other publicly available webspace).
2. Providing the image at the specified URL for download.

Periodically (or upon request), a process is run, which
- loops through ``staged_images.csv``,
- retrieving the files and uploading them to our file server (computing the [md5 hash](http://en.wikipedia.org/wiki/MD5)) on the way,
- enriching the metadata, in case the image is from a known provider (Wikimedia, Flickr, EOL, ...),
- moving the metadata from ``staged_images.csv`` to ``images.csv``, replacing the ``id``.


### Image providers

For several providers of flora and fauna imagery we provide support for downloading images
and associated metadata (by specifying matching URLs as `id` in `staged_images.csv`):

- [EOL](http://eol.org) images specified by a URL of the form `http://media.eol.org/data_objects/21916329`.
  (You typically get to a page with such a URL by clicking on any image you encounter
  while browsing EOL)
- [Flickr](https://flickr.com) images specified by a URL of the form `https://www.flickr.com/photos/damouns/78968973`,
  i.e. a photo's details page.
- [African Plants](http://www.africanplants.senckenberg.de/root/index.php) photos from Senckenberg,
  specified by an URL of the form `http://www.westafricanplants.senckenberg.de/root/index.php?page_id=14&id=722#image=26800`,
  i.e. the URL you see in your browser's location bar after clicking to enlarge an image.
- [Wikimedia](https://commons.wikimedia.org/wiki/Main_Page)
- [Flora of Zimbabwe](http://www.zimbabweflora.co.zw/) or [Flora of Mozambique](http://www.mozambiqueflora.com/)


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


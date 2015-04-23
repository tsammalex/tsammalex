from __future__ import print_function, unicode_literals, absolute_import, division
from collections import OrderedDict
import argparse

from tsammalexdata.util import data_file, jsonload, jsondump, csv_items
from tsammalexdata.gbif import GBIF
from tsammalexdata.catalogueoflife import CatalogueOfLife
from tsammalexdata.eol import EOL
from tsammalexdata.taxa import item2spec
from tsammalexdata.distribution import main


def update_taxa():
    parser = argparse.ArgumentParser(
        description="""\
Update the supplemental data for taxa from external sources.

We go through the taxa listed in taxa.csv and look for additional information at
GBIF, EOL and Catalogue Of Life.""")
    parser.add_argument("--distribution-only", action="store_true")
    args = parser.parse_args()

    if not args.distribution_only:
        fname = data_file('taxa.json')
        taxa = jsonload(fname, default=[], object_pairs_hook=OrderedDict)
        ids = set(spec['id'] for spec in taxa)

        # add stubs for new entries in taxa.csv:
        for i, item in enumerate(csv_items('taxa.csv')):
            if item['id'] not in ids:
                taxa.insert(i, item2spec(item))

        for cls in [CatalogueOfLife, GBIF, EOL]:
            with cls() as provider:
                for i, spec in enumerate(taxa):
                    if i % 500 == 0:
                        print(i)
                    provider.update_taxon(spec)

        jsondump(taxa, fname, indent=4)

    main()

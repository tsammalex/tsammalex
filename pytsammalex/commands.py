from __future__ import print_function, unicode_literals, absolute_import, division

from clldutils.path import Path

from pytsammalex.util import csv_items
from pytsammalex.gbif import GBIF, save_occurrences
from pytsammalex.catalogueoflife import CatalogueOfLife
from pytsammalex.eol import EOL
from pytsammalex.taxa import Taxa
from pytsammalex.distribution import main


def update_taxa(args):
    """
    Update the supplemental data for taxa from external sources.

    We go through the taxa listed in taxa.csv and look for additional information at
    GBIF, EOL and Catalogue Of Life.
    """
    with Taxa('taxa2.json', repos=args.tsammalex_data) as taxa:
        # add stubs for new entries in taxa.csv:
        for i, item in enumerate(csv_items('taxa.csv', repos=args.tsammalex_data)):
            taxa.add(i, item)

        for cls in [CatalogueOfLife, GBIF, EOL]:
            relpath = Path('external').joinpath(cls.__name__.lower() + '.json')
            with cls(relpath, repos=args.tsammalex_data) as provider:
                for i, spec in enumerate(taxa):
                    if i % 500 == 0:
                        print(i)
                    provider.update_taxon(spec)


def update_distribution(args):
    main()


def get_occurrences(args):
    """
    Retrieve occurrence information for each taxa from GBIF.
    """
    for item in csv_items('taxa.csv', repos=args.tsammalex_data):
        api = GBIF(Path('external').joinpath('gbif.json'), repos=args.tsammalex_data)
        save_occurrences(api, item['id'], item['scientific_name'])

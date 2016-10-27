from __future__ import print_function, unicode_literals, absolute_import, division
import os

from clldutils.path import Path
from cdstarcat.catalog import Catalog

from pytsammalex.util import csv_items, MediaCatalog, add_rows, filter_rows, data_file
from pytsammalex.gbif import GBIF, save_occurrences
from pytsammalex.catalogueoflife import CatalogueOfLife
from pytsammalex.eol import EOL
from pytsammalex.taxa import Taxa
from pytsammalex.distribution import main
from pytsammalex.image_providers import PROVIDERS


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


def upload_images(args):
    """
    tsammalex upload_images path/to/cdstar/catalog
    """
    images_path = data_file('images.csv', repos=args.tsammalex_data)
    staged_images_path = data_file('staged_images.csv', repos=args.tsammalex_data)
    checksums = set(d['id'] for d in csv_items('images.csv', repos=args.tsammalex_data))
    providers = [prov(args.tsammalex_data) for prov in PROVIDERS]
    with MediaCatalog(
            'cdstar.json', repos=args.tsammalex_data, json_opts=dict(indent=4)) as mcat:
        with Catalog(
                args.args[0],
                cdstar_url=os.environ['CDSTAR_URL'],
                cdstar_user=os.environ['CDSTAR_USER'],
                cdstar_pwd=os.environ['CDSTAR_PWD']) as cat:
            for item in csv_items('staged_images.csv', repos=args.tsammalex_data):
                id_ = item['id']
                for provider in providers:
                    if item in provider:
                        img = provider.retrieve(item, cat, checksums, mcat)
                        if img:
                            try:
                                add_rows(images_path, img.csv_row())
                            except:
                                print(img)
                                raise
                            filter_rows(staged_images_path, lambda d: d['id'] != id_)
                        break


def update_distribution(args):
    main()


def get_occurrences(args):
    """
    Retrieve occurrence information for each taxa from GBIF.
    """
    for item in csv_items('taxa.csv', repos=args.tsammalex_data):
        api = GBIF(Path('external').joinpath('gbif.json'), repos=args.tsammalex_data)
        save_occurrences(api, item['id'], item['scientific_name'])

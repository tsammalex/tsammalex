from __future__ import print_function, unicode_literals, absolute_import, division
import os

from cdstarcat.catalog import Catalog
from tqdm import tqdm

from pytsammalex.util import MediaCatalog, add_rows, filter_rows, data_file
from pytsammalex.data_providers.gbif import GBIF
from pytsammalex.data_providers.catalogueoflife import CatalogueOfLife
from pytsammalex.data_providers.eol import EOL
from pytsammalex.taxa import TaxaData
from pytsammalex import distribution
from pytsammalex.image_providers import PROVIDERS
from pytsammalex import models


def update_taxa(args):
    """
    Update the supplemental data for taxa from external sources.

    We go through the taxa listed in taxa.csv and look for additional information at
    GBIF, EOL and Catalogue Of Life.
    """
    with TaxaData(repos=args.tsammalex_data) as taxa:
        # add stubs for new entries in taxa.csv:
        for i, item in enumerate(models.CsvData('taxa', repos=args.tsammalex_data)):
            taxa.add(i, item)

        for cls in [CatalogueOfLife, GBIF, EOL]:
            print(cls.__name__)
            with cls(args.tsammalex_data) as provider:
                for spec in tqdm(taxa, leave=False):
                    provider.update_taxon(spec)


def upload_images(args):
    """
    tsammalex upload_images path/to/cdstar/catalog
    """

    images_path = data_file('images.csv', repos=args.tsammalex_data)
    staged_images_path = data_file('staged_images.csv', repos=args.tsammalex_data)
    checksums = set(d.id for d in models.CsvData('images', repos=args.tsammalex_data))
    providers = [prov(args.tsammalex_data) for prov in PROVIDERS]
    with MediaCatalog(
            'cdstar.json', repos=args.tsammalex_data, json_opts=dict(indent=4)) as mcat:
        with Catalog(
                args.args[0],
                cdstar_url=os.environ['CDSTAR_URL'],
                cdstar_user=os.environ['CDSTAR_USER'],
                cdstar_pwd=os.environ['CDSTAR_PWD']) as cat:
            for item in models.CsvData('staged_images', repos=args.tsammalex_data):
                for provider in providers:
                    if item in provider:
                        img = provider.retrieve(item, cat, checksums, mcat)
                        if img:
                            try:
                                add_rows(images_path, img.csv_row())
                            except:
                                print(img)
                                raise
                            filter_rows(staged_images_path, lambda d: d['id'] != item.id)
                        break


def update_distribution(args):
    distribution.update(args.tsammalex_data)

"""
collect data from external sources into species.json
"""
from __future__ import print_function, unicode_literals, absolute_import, division
import sys
from collections import OrderedDict

from purl import URL

from tsammalexdata.util import data_file, jsonload, jsondump, csv_items, split_ids
from tsammalexdata.gbif import GBIF
from tsammalexdata.catalogueoflife import CatalogueOfLife
from tsammalexdata.eol import EOL


def wikipedia_url(s):
    url = URL(s)
    if url.scheme() in ['http', 'https'] and 'wikipedia.' in url.host():
        return s


def item2spec(item):
    spec = OrderedDict()
    for k, v in [
        ('id', item['id']),
        ('name', item['scientific_name']),
        ('kingdom', item['kingdom'].capitalize() or None),
        ('order', item['order'].capitalize() or None),
        ('family', item['family'].capitalize() or None),
        ('genus', item['genus'].capitalize() or None),
        ('ecoregions', split_ids(item.get('ecoregions__ids', ''))),
        ('countries', split_ids(item.get('countries__ids', ''))),
        ('wikipedia_url', wikipedia_url(item.get('wikipedia_url', ''))),
        ('eol_id', None),
        ('gbif_id', None),
        ('catalogueoflife_id', None),
    ]:
        spec[k] = v
    return spec


if __name__ == '__main__':
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

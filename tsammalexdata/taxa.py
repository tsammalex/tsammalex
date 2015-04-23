"""
collect data from external sources into species.json
"""
from __future__ import print_function, unicode_literals, absolute_import, division
from collections import OrderedDict

from purl import URL

from tsammalexdata.util import split_ids


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

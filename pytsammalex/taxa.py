"""
collect data from external sources into species.json
"""
from __future__ import print_function, unicode_literals, absolute_import, division
from collections import OrderedDict

from purl import URL

from pytsammalex.util import split_ids, JsonData, REPOS


def wikipedia_url(s):
    url = URL(s)
    if url.scheme() in ['http', 'https'] and 'wikipedia.' in url.host():
        return s


class Taxa(JsonData):
    def __init__(self, path, repos=REPOS):
        JsonData.__init__(
            self, path, repos=repos, container_cls=list, json_opts=dict(indent=4))
        self._ids = set(spec['id'] for spec in self._items)

    def __contains__(self, item):
        return item in self._ids

    def __iter__(self):
        return iter(self._items)

    def add(self, index, item):
        """
        Add a taxon item as read from taxa.csv to the catalog, if it is not already in.

        :param index: Position in the list
        :param item: `dict` as read from taxa.csv
        """
        if item['id'] not in self:
            self._items.insert(
                index,
                OrderedDict([
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
                ]))
            self._ids.add(item['id'])

from __future__ import print_function, unicode_literals

from pytsammalex.data_providers.base import DataProvider


class GBIF(DataProvider):
    def _get(self, path, **kw):
        return self.get('http://api.gbif.org/v1/' + path, type_='json', **kw)

    def identify(self, name):
        res = self._get('species/match', name=name)
        if 'rank' not in res:
            return  # pragma: no cover
        rank = res['rank'].lower()
        if rank in ['subspecies', 'variety'] and rank + 'Key' not in res:
            rank = 'species'  # pragma: no cover
        try:
            return res[rank + 'Key']
        except KeyError:  # pragma: no cover
            return

    def metadata(self, id):
        kw = dict(
            taxonKey=id,
            basisOfRecord='HUMAN_OBSERVATION',
            hasCoordinate='true',
            limit=100)
        return self._get('occurrence/search', **kw)

    def update(self, taxon, data):
        if data.get('results'):
            result = data['results'][0]
            for key in 'kingdom phylum class order genus family'.split():
                if result.get(key):
                    taxon[key] = result[key]
            if 'taxonRank' in result:
                taxon['taxonRank'] = result['taxonRank'].lower()

    def get_occurrences(self, item):
        return self.cached_metadata(item.id, name=item.scientific_name)

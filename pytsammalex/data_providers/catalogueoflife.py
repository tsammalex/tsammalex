"""
Functionality to retrieve information from the Catalogue of Life Web Service

.. seealso:: http://webservice.catalogueoflife.org/col/webservice
"""
from __future__ import print_function, unicode_literals, absolute_import, division

from six import text_type

from pytsammalex.util import unique
from pytsammalex.data_providers.base import DataProvider


def text(e, ee):
    ee = e.find(ee)
    return (ee.text if ee is not None else '') or ''


class CatalogueOfLife(DataProvider):
    def _get(self, **kw):
        try:
            return self.get(
                'http://www.catalogueoflife.org/col/webservice',
                type_='xml',
                **kw).find('result')
        except:  # pragma: no cover
            return None

    def identify(self, name):
        result = self._get(name=name)
        if result:
            if text(result, 'name_status') == 'accepted name':
                return text(result, 'id')
            if result.find('accepted_name'):
                return text(result.find('accepted_name'), 'id')

    def metadata(self, id_):
        result = self._get(id=id_, response='full')
        if result:
            # classification: taxon.id name rank url
            # synonyms: synonym.name
            res = {k: text(result, k) for k in 'genus species author url'.split()}
            res['distribution'] = unique(
                region.split()[0] for region in
                text(result, 'distribution').split('; ') if region)
            if result.find('classification'):
                res['classification'] = {
                    t.rank.lower(): t.as_dict() for t in
                    [Taxon(e) for e in result.find('classification').findall('taxon')]}
            if result.find('synonyms'):
                res['synonyms'] = filter(
                    None,
                    [text(e, 'name') for e in result.find('synonyms').findall('synonym')])
            return {k: v for k, v in res.items() if v}

    def update(self, taxon, data):
        if 'distribution' in data:
            taxon['tdwgregions'] = unique(data['distribution'])
        classification = data.get('classification', {})
        for key in 'kingdom phylum class order genus family'.split():
            if classification.get(key):
                taxon[key] = classification[key]['name']
        taxon[self.name + '_url'] = data['url']
        if 'author' in data:
            taxon['description'] = data['author']


class Taxon(object):
    def __init__(self, e):
        for attr in 'id name rank url'.split():
            setattr(self, attr, text(e, attr))

    def as_dict(self):
        return dict(id=self.id, name=self.name, url=self.url)

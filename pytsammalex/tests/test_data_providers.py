# coding: utf8
from __future__ import unicode_literals, print_function, division

from clldutils.testing import WithTempDir
from mock import patch

from pytsammalex.tests.util import MockRequests, MockResponse, create_repos, fixtures
from pytsammalex.models import Taxa


class Tests(WithTempDir):
    def test_DataProvider(self):
        from pytsammalex.data_providers.base import DataProvider

        prov = DataProvider(self.tmp_path())
        self.assertEqual(prov.name, 'dataprovider')

        with patch('pytsammalex.util.requests', MockRequests()):
            prov = DataProvider(self.tmp_path())
            self.assertEqual(prov.get(None, type_='json')['a'], 'b')
            self.assertEqual(prov.get(None, type_='xml').tag, 'a')
            self.assertIsInstance(prov.get(None), MockResponse)
            self.assertRaises(NotImplementedError, prov.identify, None)
            self.assertRaises(NotImplementedError, prov.metadata, None)
            self.assertRaises(NotImplementedError, prov.update, None, None)
            self.assertIsNone(prov.cached_metadata(None, None))
            prov.items[1] = 1
            self.assertEqual(prov.cached_metadata(1, None), 1)

    def test_Catalogueoflife(self):
        from pytsammalex.data_providers.catalogueoflife import CatalogueOfLife

        data = fixtures('data_providers', 'catalogueoflife')
        id_ = '9249d9473aac5c8e99fb9d758ced91ec'
        repos = create_repos(self.tmp_path())
        with patch('pytsammalex.util.requests', MockRequests(content=data['identify'])):
            prov = CatalogueOfLife(repos)
            self.assertEqual(prov.identify('x'), id_)

        with patch('pytsammalex.util.requests', MockRequests(content=data['metadata'])):
            prov = CatalogueOfLife(repos)
            md = prov.cached_metadata('test', id_)
            taxon = {}
            prov.update(taxon, md)
            self.assertEqual(
                taxon,
                {
                    'catalogueoflife_url': 'http://www.catalogueoflife.org/col/browse/tree/id/9249d9473aac5c8e99fb9d758ced91ec',
                    'class': 'Mammalia',
                    'family': 'Felidae',
                    'kingdom': 'Animalia',
                    'order': 'Carnivora',
                    'phylum': 'Chordata'})

    def test_Gbif(self):
        from pytsammalex.data_providers.gbif import GBIF

        data = fixtures('data_providers', 'gbif')
        with patch(
                'pytsammalex.util.requests',
                MockRequests(json=[data['identify'], data['metadata']])):
            prov = GBIF(create_repos(self.tmp_path()))
            taxon = {'id': 'pantheraleo', 'name': 'Panthera leo'}
            prov.update_taxon(taxon)
            self.assertEqual(
                taxon,
                {
                    'gbif_id': 5219404,
                    'id': 'pantheraleo',
                    'name': 'Panthera leo',
                    'class': 'Mammalia',
                    'family': 'Felidae',
                    'genus': 'Panthera',
                    'kingdom': 'Animalia',
                    'order': 'Carnivora',
                    'phylum': 'Chordata',
                    'taxonRank': 'species'})
            res = prov.get_occurrences(Taxa(*'pantheraleo,,,,,,,,,,,,,,,,,'.split(',')))
            self.assertEqual(res['count'], 576)

    def test_Eol(self):
        from pytsammalex.data_providers.eol import EOL

        data = fixtures('data_providers', 'eol')
        with patch(
            'pytsammalex.util.requests',
            MockRequests(json=[data['identify'], data['metadata'], data['hierarchy']])
        ):
            prov = EOL(create_repos(self.tmp_path()))
            taxon = {'id': 'pantheraleo', 'name': 'Panthera leo'}
            prov.update_taxon(taxon)
            self.assertEqual(
                taxon,
                {
                    'eol_id': 328672,
                    'english_name': 'Asian lion',
                    'id': 'pantheraleo',
                    'name': 'Panthera leo',
                    'class': 'Mammalia',
                    'family': 'Felidae',
                    'genus': 'Panthera',
                    'kingdom': 'Animalia',
                    'order': 'Carnivora',
                    'phylum': 'Chordata',
                    'taxonRank': 'species'})

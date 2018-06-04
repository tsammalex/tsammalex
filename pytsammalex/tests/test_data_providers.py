# coding: utf8
from __future__ import unicode_literals, print_function, division

import pytest
from mock import patch

from pytsammalex.data_providers.base import DataProvider
from pytsammalex.data_providers.catalogueoflife import CatalogueOfLife
from pytsammalex.data_providers.eol import EOL
from pytsammalex.data_providers.gbif import GBIF
from pytsammalex.tests.util import MockRequests, MockResponse, create_repos, \
    fixtures

from clldutils.path import Path


def test_data_provider(tmpdir):
    prov = DataProvider(Path(tmpdir))
    assert (prov.name == 'dataprovider')

    with patch('pytsammalex.util.requests', MockRequests()):
        prov = DataProvider(Path(tmpdir))
        assert (prov.get(None, type_='json')['a'] == 'b')
        assert (prov.get(None, type_='xml').tag == 'a')
        assert (isinstance(prov.get(None), MockResponse))

        with pytest.raises(NotImplementedError):
            prov.identify(None)

        with pytest.raises(NotImplementedError):
            prov.metadata(None)

        with pytest.raises(NotImplementedError):
            prov.update(None, None)

        assert (prov.cached_metadata(None, None) is None)

        prov.items[1] = 1
        assert (prov.cached_metadata(1, None) == 1)


def test_catalogue_of_life(tmpdir):
    data = fixtures('data_providers', 'catalogueoflife')
    id_ = '9249d9473aac5c8e99fb9d758ced91ec'
    repos = create_repos(tmpdir)

    with patch('pytsammalex.util.requests',
               MockRequests(content=data['identify'])):
        prov = CatalogueOfLife(Path(repos))
        assert (prov.identify('x') == id_)

    with patch('pytsammalex.util.requests',
               MockRequests(content=data['metadata'])):
        prov = CatalogueOfLife(Path(repos))
        md = prov.cached_metadata('test', id_)
        taxon = {}
        prov.update(taxon, md)
        assert (
                taxon ==
                {
                    'catalogueoflife_url': 'http://www.catalogueoflife.org/col/'
                                           'browse/tree/id/'
                                           '9249d9473aac5c8e99fb9d758ced91ec',
                    'class': 'Mammalia',
                    'family': 'Felidae',
                    'kingdom': 'Animalia',
                    'order': 'Carnivora',
                    'phylum': 'Chordata'})


def test_gbif(tmpdir):
    data = fixtures('data_providers', 'gbif')
    with patch(
            'pytsammalex.util.requests',
            MockRequests(json=[data['identify'], data['metadata']])):
        prov = GBIF(Path(create_repos(tmpdir)))
        taxon = {'id': 'pantheraleo', 'name': 'Panthera leo'}
        prov.update_taxon(taxon)
        assert (
                taxon ==
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


def test_eol(tmpdir):
    data = fixtures('data_providers', 'eol')
    with patch(
            'pytsammalex.util.requests',
            MockRequests(
                json=[data['identify'], data['metadata'], data['hierarchy']])
    ):
        prov = EOL(Path(create_repos(tmpdir)))
        taxon = {'id': 'pantheraleo', 'name': 'Panthera leo'}
        prov.update_taxon(taxon)
        assert (
                taxon ==
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

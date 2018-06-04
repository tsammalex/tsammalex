# coding: utf8
from __future__ import unicode_literals, print_function, division

from clldutils.path import Path

from pytsammalex.models import Taxa
from pytsammalex.taxa import TaxaData
from pytsammalex.tests.util import create_repos


def test_taxa_data(tmpdir):
    repos = Path(create_repos(tmpdir))

    with TaxaData(repos) as taxa:
        taxa.add(0, Taxa.fromdict({'id': 'abc'}))

    assert 'abc' in TaxaData(repos)

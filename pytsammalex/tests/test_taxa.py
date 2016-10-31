# coding: utf8
from __future__ import unicode_literals, print_function, division

from clldutils.testing import WithTempDir

from pytsammalex.tests.util import create_repos
from pytsammalex.models import Taxa


class Tests(WithTempDir):
    def test_TaxaData(self):
        from pytsammalex.taxa import TaxaData

        repos = create_repos(self.tmp_path())
        with TaxaData(repos) as taxa:
            taxa.add(0, Taxa.fromdict({'id': 'abc'}))
        self.assertIn('abc', TaxaData(repos))

# coding: utf8
from __future__ import unicode_literals, print_function, division

from mock import patch, Mock
from clldutils.testing import WithTempDir

from pytsammalex.tests.util import create_repos
from pytsammalex.models import CsvData


class Tests(WithTempDir):
    def test_update(self):
        from pytsammalex.distribution import update

        repos = create_repos(self.tmp_path())
        with patch.multiple(
                'pytsammalex.distribution',
                shape=Mock(return_value=Mock(return_value=True)),
                Point=Mock()):
            update(repos, verbose=False)

        data = CsvData('distribution', repos=repos)
        self.assertEqual(len(data), 1)
        self.assertEqual(
            data.items[0].ecoregions__ids,
            [
                'AT0110',
                'AT0111',
                'AT0112',
                'AT0113',
                'AT0114',
                'AT0115',
                'AT0116',
                'AT0117',
                'AT0118',
                'AT0119'])

# coding: utf8
from __future__ import unicode_literals, print_function, division

from clldutils.testing import WithTempDir
from clldutils.dsv import reader

from pytsammalex.tests.util import create_repos, MOCK_CDSTAR_OBJECT


class Tests(WithTempDir):
    def test_add_delete_rows(self):
        from pytsammalex.util import add_rows, filter_rows

        csv_path = self.tmp_path('test.csv')
        add_rows(csv_path, ['a', 'b'], [1, 2], [3, 4])
        self.assertEqual(len(list(reader(csv_path, dicts=True))), 2)
        filter_rows(csv_path, lambda item: item['a'] == '1')
        self.assertEqual(len(list(reader(csv_path, dicts=True))), 1)
        add_rows(csv_path, [1, 2], [3, 4])
        self.assertEqual(len(list(reader(csv_path, dicts=True))), 3)

    def test_JsonData(self):
        from pytsammalex.util import JsonData, data_file

        tmpdir = create_repos(self.tmp_path())
        with JsonData('test.json', repos=tmpdir) as jdat:
            jdat['a'] = 1
        self.assertTrue(data_file('test.json', repos=tmpdir).exists())
        with JsonData('test.json', repos=tmpdir) as jdat:
            self.assertEqual(len(jdat), 1)
            self.assertEqual(jdat['a'], 1)

    def test_ExternalProviderMixin(self):
        from pytsammalex.util import ExternalProviderMixin

        prov = ExternalProviderMixin()
        self.assertEqual(prov.bs('<a href="x">t</a>').find('a').get('href'), 'x')

    def test_MediaCatalog(self):
        from pytsammalex.util import MediaCatalog

        cat = MediaCatalog('test.json', repos=self.tmp_path())
        cat.add(MOCK_CDSTAR_OBJECT)

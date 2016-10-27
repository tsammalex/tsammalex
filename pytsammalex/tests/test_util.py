# coding: utf8
from __future__ import unicode_literals, print_function, division

from clldutils.testing import WithTempDir
from clldutils.dsv import UnicodeWriter, reader


class Tests(WithTempDir):
    def test_add_delete_rows(self):
        from pytsammalex.util import add_rows, filter_rows

        csv_path = self.tmp_path('test.csv')
        add_rows(csv_path, ['a', 'b'], [1, 2], [3, 4])
        self.assertEqual(len(list(reader(csv_path, dicts=True))), 2)
        filter_rows(csv_path, lambda item: item['a'] == '1')
        self.assertEqual(len(list(reader(csv_path, dicts=True))), 1)

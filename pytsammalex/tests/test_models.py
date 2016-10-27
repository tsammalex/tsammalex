# coding: utf8
from __future__ import unicode_literals, print_function, division
from unittest import TestCase


class Tests(TestCase):
    def test_Images(self):
        from pytsammalex.models import Images

        row = "47a4a90a6fb76d027e7db2d383973e1d,motacillaflava,general;thumbnail1," \
              "image/jpeg,,,,,50.567634 30.301384,https://creativecommons.org/," \
              "http://commons.wikimedia.org/wiki/File:Motacilla_flava_Horenka2.jpg,"\
            .split(',')
        self.assertEqual(Images(*row).csv_row(), row)

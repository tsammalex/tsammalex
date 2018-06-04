# coding: utf8
from __future__ import unicode_literals, print_function, division

from clldutils.path import Path
from mock import patch, Mock

from pytsammalex.distribution import update
from pytsammalex.models import CsvData
from pytsammalex.tests.util import create_repos


def test_update(tmpdir):
    repos = create_repos(tmpdir)

    with patch.multiple('pytsammalex.distribution',
                        shape=Mock(return_value=Mock(return_value=True)),
                        Point=Mock()):
        update(Path(repos), log=Mock())

    data = CsvData('distribution', repos=Path(repos))
    assert (len(data) == 1)
    assert (
            data.items[0].ecoregions__ids ==
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

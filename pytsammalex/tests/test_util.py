# coding: utf8
from __future__ import unicode_literals, print_function, division

from clldutils.dsv import reader
from clldutils.path import Path

from pytsammalex.tests.util import create_repos, MOCK_CDSTAR_OBJECT
from pytsammalex.util import add_rows, filter_rows, JsonData, data_file, \
    ExternalProviderMixin, MediaCatalog


def test_add_delete_rows(tmpdir):
    csv_path = Path(tmpdir.join('test.csv'))
    add_rows(csv_path, ['a', 'b'], [1, 2], [3, 4])
    assert (len(list(reader(csv_path, dicts=True))) == 2)

    filter_rows(csv_path, lambda item: item['a'] == '1')
    assert (len(list(reader(csv_path, dicts=True))) == 1)

    add_rows(csv_path, [1, 2], [3, 4])
    assert (len(list(reader(csv_path, dicts=True))) == 3)


def test_json_data(tmpdir):
    tmp_ = create_repos(tmpdir)

    with JsonData('test.json', repos=Path(tmp_)) as jdat:
        jdat['a'] = 1

    assert (data_file('test.json', repos=Path(tmp_)).exists() is True)

    with JsonData('test.json', repos=Path(tmp_)) as jdat:
        assert (len(jdat) == 1)
        assert (jdat['a'] == 1)


def test_external_provider_mixin():
    prov = ExternalProviderMixin()
    assert (prov.bs('<a href="x">t</a>').find('a').get('href') == 'x')


def test_media_catalog(tmpdir):
    cat = MediaCatalog('test.json', repos=Path(tmpdir))
    cat.add(MOCK_CDSTAR_OBJECT)

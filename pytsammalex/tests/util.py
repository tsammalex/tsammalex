# coding: utf8
from __future__ import unicode_literals, print_function, division

from clldutils.path import Path, copy
from clldutils import jsonlib
from cdstarcat.catalog import Object, Bitstream

MOCK_CDSTAR_OBJECT = Object(
    '12345-1234-1234-1234-1',
    [
        Bitstream('thumbnail', 1, 2, 3, 4, 5),
        Bitstream('web', 1, 2, 3, 4, 5),
        Bitstream('other', 1, 2, 3, 4, 5),
    ],
    {},
)


class MockResponse(object):
    headers = {'content-type': 'image/jpeg'}

    def __init__(self, json=None, content='<a>b</a>', text=''):
        self._json = json or {"a": "b"}
        self.content = content
        self.text = text

    def json(self):
        return self._json


class MockRequests(object):
    def __init__(self, json=None, content=None, text=None):
        self._json = json or {"a": "b"}
        self._content = content or b'<a>b</a>'
        self._text = text

    def get(self, *args, **kw):
        if isinstance(self._json, list):
            json = self._json.pop(0)
        else:
            json = self._json
        return MockResponse(json=json, content=self._content, text=self._text)


def fixture_path(*comps):
    return Path(__file__).parent.joinpath('fixtures', *comps)


def fixtures(type_, name):
    res = {}
    for fname in fixture_path(type_).iterdir():
        name_, key = fname.stem.split('_')
        if name_ == name:
            value = fname
            if fname.suffix == '.json':
                value = jsonlib.load(fname)
            elif fname.suffix == '.html':
                with fname.open(encoding='utf8') as fp:
                    value = fp.read()
            elif fname.suffix == '.xml':
                with open(fname.as_posix(), 'rb') as fp:
                    value = fp.read()
            res[key] = value
    return res


def create_repos(dir_):
    tsammalexdata = dir_.joinpath('tsammalexdata')
    tsammalexdata.mkdir()
    data = tsammalexdata.joinpath('data')
    data.mkdir()
    with data.joinpath('test.csv').open('w', encoding='utf8') as fp:
        fp.write("""\
a,b,c
1,2,3
4,5,6""")
    with data.joinpath('distribution.csv').open('w', encoding='utf8') as fp:
        fp.write("id,coregions__ids,countries_ids")
    copy(fixture_path('test_ecoregions.json'), data.joinpath('ecoregions.json'))
    external = data.joinpath('external')
    external.mkdir()
    with external.joinpath('test.csv').open('w', encoding='utf8') as fp:
        fp.write("""\
a,b,c
1,2,3
4,5,6""")
    external.joinpath('gbif').mkdir()
    occurrences = fixture_path('abelmoschusesculentus.json')
    copy(occurrences, external.joinpath('gbif', occurrences.name))
    return dir_

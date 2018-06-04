from __future__ import unicode_literals, division, print_function
import sys
import re
from collections import OrderedDict
from xml.etree import cElementTree as et

from clldutils import jsonlib
from clldutils import dsv
from clldutils.path import Path
import requests
import urllib3
from bs4 import BeautifulSoup

import pytsammalex


urllib3.disable_warnings(urllib3.exceptions.InsecurePlatformWarning)
urllib3.disable_warnings(urllib3.exceptions.SNIMissingWarning)


REPOS = Path(pytsammalex.__file__).parent.parent

PY3 = sys.version_info[0] == 3
ID_SEP_PATTERN = re.compile('\.|,|;')


def unique(iterable):
    return list(sorted(set(i for i in iterable if i)))


def split_ids(s, sep=ID_SEP_PATTERN):
    return unique(id_.strip() for id_ in sep.split(s) if id_.strip())


def data_file(*comps, **kw):
    return Path(kw.pop('repos', REPOS).joinpath('tsammalexdata', 'data', *comps))


add_rows = dsv.add_rows
filter_rows = dsv.filter_rows_as_dict


class DataManager(object):
    """
    Context manager mediating access to data stored in a JSON file.
    """
    def __init__(self, path, repos):
        self.path = data_file(path, repos=repos)
        self.repos = repos
        self.items = []

    def __iter__(self):
        return iter(self.items)

    def __len__(self):
        return len(self.items)

    def __enter__(self):
        return self

    def __getitem__(self, item):
        return self.items[item]

    def __setitem__(self, key, value):
        self.items[key] = value

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.write()

    def write(self):
        raise NotImplementedError()  # pragma: no cover


class JsonData(DataManager):
    """
    Context manager mediating access to data stored in a JSON file.
    """
    def __init__(self, path, repos=REPOS, container_cls=dict, json_opts=None):
        DataManager.__init__(self, path, repos)
        if self.path.exists():
            self.items = jsonlib.load(self.path, object_pairs_hook=OrderedDict)
        else:
            self.items = container_cls()
        self._json_opts = json_opts or {}

    def write(self):
        jsonlib.dump(self.items, self.path, **self._json_opts)


class ExternalProviderMixin(object):
    @staticmethod
    def get(url, type_=None, **params):
        res = requests.get(url, params=params)
        if type_ == 'json':
            return res.json()
        if type_ == 'xml':
            return et.fromstring(res.content)
        return res

    @staticmethod
    def bs(markup):
        return BeautifulSoup(markup, 'html.parser')

    def identify(self, name):
        raise NotImplementedError()

    def metadata(self, id):
        raise NotImplementedError()


class MediaCatalog(JsonData):
    def add(self, obj):
        """
        :param obj: A `cdstarcat.catalog.Object` instance
        :return:
        """
        bitstreams = {bs.id.split('.')[0]: bs for bs in obj.bitstreams}
        res = OrderedDict([('objid', obj.id)])
        thumbnail = bitstreams.pop('thumbnail')
        web = bitstreams.pop('web')
        assert len(bitstreams) == 1
        original = list(bitstreams.values())[0]
        res['original'] = original.id
        res['size'] = original.size
        res['thumbnail'] = thumbnail.id
        res['web'] = web.id
        self.items[original.md5] = res

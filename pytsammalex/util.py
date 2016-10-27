from __future__ import unicode_literals, division, print_function
import sys
import re
from xml.etree import cElementTree as et
from itertools import chain
from collections import OrderedDict

import requests
from purl import URL
from clldutils import jsonlib
from clldutils import dsv
from clldutils.path import Path, move

import pytsammalex


REPOS = Path(pytsammalex.__file__).parent.parent

PY3 = sys.version_info[0] == 3
ID_SEP_PATTERN = re.compile('\.|,|;')


def unique(iterable):
    return list(sorted(set(i for i in iterable if i)))


def split_ids(s, sep=ID_SEP_PATTERN):
    return unique(id_.strip() for id_ in sep.split(s) if id_.strip())


def data_file(*comps, **kw):
    return kw.pop('repos', REPOS).joinpath('tsammalexdata', 'data', *comps)


def csv_items(name, repos=REPOS):
    data = data_file(name, repos=repos)
    if data.is_dir():
        fnames = list(data.glob('*.csv'))
    elif data.is_file():
        fnames = [data]
    elif data.parent.joinpath(data.name + '.csv').is_file():
        fnames = [data.parent.joinpath(data.name + '.csv')]
    else:
        raise ValueError(name)

    return list(chain(*[dsv.reader(fname, dicts=True) for fname in fnames]))


def add_rows(fname, *rows):
    tmp = fname.parent.joinpath('.tmp.' + fname.name)

    with dsv.UnicodeWriter(tmp) as writer:
        if fname.exists():
            with dsv.UnicodeReader(fname) as reader_:
                for row in reader_:
                    writer.writerow(row)
        writer.writerows(rows)
    move(tmp, fname)


class Filter(object):
    def __init__(self, filter_):
        self.header = None
        self.filter = filter_

    def __call__(self, i, row):
        if i == 0:
            self.header = row
            return row
        if row:
            item = dict(zip(self.header, row))
            try:
                if self.filter(item):
                    return row
            except:
                print(self.header)
                print(row)
                print(item)
                raise


def filter_rows(fname, filter_):
    dsv.rewrite(fname, Filter(filter_), lineterminator='\r\n')


class JsonData(object):
    """
    Context manager mediating access to data stored in a JSON file.
    """
    def __init__(self, path, repos=REPOS, container_cls=dict, json_opts=None):
        self.path = data_file(path, repos=repos)
        self.repos = repos
        if self.path.exists():
            self.items = jsonlib.load(self.path, object_pairs_hook=OrderedDict)
        else:
            self.items = container_cls()
        self._json_opts = json_opts or {}

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        jsonlib.dump(self.items, self.path, **self._json_opts)


class DataProvider(JsonData):
    host = 'example.org'
    scheme = 'http'

    @property
    def name(self):
        return self.__class__.__name__.lower()

    def url(self, path):
        return URL(scheme=self.scheme, host=self.host).path(path)

    def get(self, path, type='json', **params):
        res = requests.get(self.url(path), params=params)
        if type == 'json':
            return res.json()
        if type == 'xml':
            return et.fromstring(res.content)
        return res

    def get_id(self, name):
        raise NotImplementedError()

    def get_info(self, id):
        raise NotImplementedError()

    def cli(self, arg):
        try:
            int(arg)
            return self.get_info(arg)
        except ValueError:
            return self.get_id(arg)

    def get_cached(self, sid, id, refresh=False):
        if data_file('external', self.name, repos=self.repos).is_dir():
            fname = data_file('external', self.name, sid + '.json', repos=self.repos)
            if not fname.exists() or refresh:
                try:
                    data = self.get_info(id)
                except:
                    data = None
                if not data:
                    return
                jsonlib.dump(data, fname)
                return data
            return jsonlib.load(fname)

        if sid not in self.items or refresh:
            try:
                self.items[sid] = self.get_info(id)
            except:
                return
        return self.items[sid]

    def update(self, taxon, data):
        raise NotImplementedError()

    def update_taxon(self, taxon):
        # Try to find a provider-specific ID:
        if not taxon[self.name + '_id']:
            taxon[self.name + '_id'] = self.get_id(taxon['name'])
        if not taxon[self.name + '_id']:
            return False

        # Use this ID to fetch new data in case nothing is cached for sid:
        data = self.get_cached(taxon['id'], taxon[self.name + '_id'])
        if data:
            self.update(taxon, data)
            return True
        return False

    def refresh(self, sid, id):
        with self as api:
            api.get_cached(sid, id, refresh=True)


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
        original = bitstreams.values()[0]
        res['original'] = original.id
        res['size'] = original.size
        res['thumbnail'] = thumbnail.id
        res['web'] = web.id
        self.items[original.md5] = res

# coding: utf8
from __future__ import unicode_literals, print_function, division

from clldutils.path import Path
from clldutils import jsonlib

from pytsammalex.util import JsonData, data_file, ExternalProviderMixin


class DataProvider(JsonData, ExternalProviderMixin):
    def __init__(self, repos):
        JsonData.__init__(
            self, Path('external').joinpath(self.name + '.json'), repos=repos)

    @property
    def name(self):
        return self.__class__.__name__.lower()

    @property
    def attr_name(self):
        return self.name + '_id'

    def cached_metadata(self, sid, id=None, name=None, refresh=False):
        if data_file('external', self.name, repos=self.repos).is_dir():
            fname = data_file('external', self.name, sid + '.json', repos=self.repos)
            if not fname.exists() or refresh:
                try:
                    data = self.metadata(id or self.identify(name))
                except:  # pragma: no cover
                    data = None
                if not data:
                    return  # pragma: no cover
                jsonlib.dump(data, fname)
                return data
            return jsonlib.load(fname)

        if sid not in self.items or refresh:
            try:
                self.items[sid] = self.metadata(id or self.identify(name))
            except:
                return
        return self.items[sid]

    def update(self, taxon, data):
        raise NotImplementedError()

    def update_taxon(self, taxon):
        # Try to find a provider-specific ID:
        if not taxon.get(self.attr_name):
            taxon[self.attr_name] = self.identify(taxon['name'])
        id_ = taxon.get(self.attr_name)
        if id_ is None:
            return False  # pragma: no cover

        # Use this ID to fetch new data in case nothing is cached for sid:
        data = self.cached_metadata(taxon['id'], id_)
        if data:
            self.update(taxon, data)
            return True
        return False  # pragma: no cover

    def refresh(self, sid, id):  # pragma: no cover
        with self as api:
            api.cached_metadata(sid, id, refresh=True)

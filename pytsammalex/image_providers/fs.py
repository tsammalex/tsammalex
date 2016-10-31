# coding: utf8
from __future__ import unicode_literals, print_function, division

from pytsammalex.image_providers.base import ImageProvider
from pytsammalex.util import data_file


class LocalFiles(ImageProvider):
    def identify(self, item):
        p = data_file('staged_images', item.id, repos=self.repos)
        if p.exists():
            return p

    def metadata(self, item):
        item['source_url'] = self.identify(item)
        return item

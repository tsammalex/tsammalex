# coding: utf8
from __future__ import unicode_literals, print_function, division
import re
from xml.etree import cElementTree as et

from pytsammalex.image_providers.base import ImageProvider


class Wikimedia(ImageProvider):
    __example__ = ('http://commons.wikimedia.org/wiki/File:Alcelaphus_caama.jpg', {})

    filename_pattern = re.compile("(?P<fname>[a-zA-Z\-_,'\(\)%0-9]+\.(jpg|png|JPG))$")
    license_pattern = re.compile('CC\-(?P<clauses>[A-Z\-]+)\-(?P<version>[0-9\.]+)')
    license_map = {
        'PD-user': 'http://en.wikipedia.org/wiki/Public_domain',
        'PD 1923': 'http://en.wikipedia.org/wiki/Public_domain',
        'CC-PD-Mark': 'http://en.wikipedia.org/wiki/Public_domain',
        'PD other reasons': 'http://en.wikipedia.org/wiki/Public_domain',
        #'PD-user': 'http://en.wikipedia.org/wiki/Public_domain',
    }

    def identify(self, item):
        """http://commons.wikimedia.org/wiki/File:Alcelaphus_caama.jpg
        """
        url, host, comps = self.url_parts(item.id)
        if not host.endswith('wikimedia.org'):
            return
        if comps[0] == 'wiki':
            if 'File:' in comps[1]:
                return comps[1].split('File:')[1]
            return
        for comp in comps:
            m = self.filename_pattern.search(comp)
            if m:
                return m.group('fname')

    def metadata(self, item):
        """
        http://tools.wmflabs.org/magnus-toolserver/commonsapi.php?image=Alcelaphus_caama.jpg
        """
        def text(e):
            if e and e.text:
                return self.bs(e.text).string

        id_ = self.identify(item)
        info = et.fromstring(self.get(
            'http://tools.wmflabs.org/magnus-toolserver/commonsapi.php',
            params=dict(image=id_)).content)
        try:
            res = dict(
                creator=text(info.find('file/author')),
                source=info.find('file/urls/description').text,
                source_url=info.find('file/urls/file').text,
                permission=info.find('licenses/license/name').text)
        except AttributeError:
            return {}
        if info.find('file/date'):
            res['date'] = text(info.find('file/date'))
        loc = info.find('file/location')
        if loc:
            res.update(longitude=loc.find('lon').text, latitude=loc.find('lat').text)
        match = self.license_pattern.match(res['permission'])
        if match:
            res['permission'] = 'https://creativecommons.org/licenses/%s/%s/' \
                                % (match.group('clauses').lower(), match.group('version'))
        else:
            res['permission'] = self.license_map.get(res['permission'], res['permission'])
        return res

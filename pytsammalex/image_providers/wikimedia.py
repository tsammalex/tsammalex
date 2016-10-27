# coding: utf8
from __future__ import unicode_literals, print_function, division
import re
from xml.etree import cElementTree as et

import requests

from pytsammalex.images import ImageProvider


class Wikimedia(ImageProvider):
    filename_pattern = re.compile("(?P<fname>[a-zA-Z\-_,'\(\)%0-9]+\.(jpg|png|JPG))$")
    license_pattern = re.compile('CC\-(?P<clauses>[A-Z\-]+)\-(?P<version>[0-9\.]+)')
    license_map = {
        'PD-user': 'http://en.wikipedia.org/wiki/Public_domain',
        'PD 1923': 'http://en.wikipedia.org/wiki/Public_domain',
        'CC-PD-Mark': 'http://en.wikipedia.org/wiki/Public_domain',
        'PD other reasons': 'http://en.wikipedia.org/wiki/Public_domain',
        #'PD-user': 'http://en.wikipedia.org/wiki/Public_domain',
    }

    def metadata(self, item):
        """
    http://tools.wmflabs.org/magnus-toolserver/commonsapi.php?image=Alcelaphus_caama.jpg

    <?xml version="1.0" encoding="UTF-8"?>
    <response version="0.92">
        <file>
            <name>Alcelaphus caama.jpg</name>
            <title>File:Alcelaphus_caama.jpg</title>
            <urls>
                <file>http://upload.wikimedia.org/wikipedia/commons/1/1d/Alcelaphus_caama.jpg</file>
                <description>http://commons.wikimedia.org/wiki/File:Alcelaphus_caama.jpg</description>
            </urls>
            <size>3485152</size>
            <width>3085</width>
            <height>2314</height>
            <uploader>Lycaon</uploader>
            <upload_date>2008-11-29T08:42:17Z</upload_date>
            <sha1>718624712e4d7a76f5521904a795c81ae55363ee</sha1>
            <location>
                <lat>-19.216961</lat>
                <lon>16.174706</lon>
            </location>
            <date>&lt;span style="white-space:nowrap"&gt;&lt;time class="dtstart" datetime="2007-06-29"&gt;29 June 2007&lt;/time&gt;&lt;/span&gt;</date>
            <author>&lt;span class="fn value"&gt;&lt;a href="http://commons.wikimedia.org/wiki/User:Biopics" title="User:Biopics"&gt;Hans Hillewaert&lt;/a&gt;&lt;/span&gt;</author>
            <source>&lt;span class="int-own-work"&gt;Own work&lt;/span&gt;</source>
        </file>
        <licenses>
            <license>
                <name>CC-BY-SA-4.0</name>
            </license>
        </licenses>
    </response>
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

    def identify(self, item):
        """http://commons.wikimedia.org/wiki/File:Alcelaphus_caama.jpg
        """
        url, host, comps = ImageProvider.url_parts(item)
        if not host.endswith('wikimedia.org'):
            return
        if comps[0] == 'wiki':
            if 'File:' in comps[1]:
                return comps[1].split('File:')[1]
            else:
                return
        for comp in comps:
            m = self.filename_pattern.search(comp)
            if m:
                return m.group('fname')

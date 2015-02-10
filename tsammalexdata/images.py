import os
import sys
import json
from xml.etree import cElementTree as et
import re
from hashlib import md5
import shutil

from bs4 import BeautifulSoup
import requests
from purl import URL
import flickrapi
from dateutil.parser import parse

from tsammalexdata.util import csv_items, data_file, jsondump, jsonload, visit


class DataProvider(object):
    @staticmethod
    def date(s):
        return str(parse(s)).split()[0]

    def id_from_url(self, url):
        raise NotImplementedError()

    def info_for_id(self, id_):
        raise NotImplementedError

    def postprocess(self, res):
        new = {}
        for k, v in res.items():
            if k == 'date' and v:
                v = self.date(v)
            if k in ['latitude', 'longitude']:
                v = float(v)
            if v:
                new[k] = v
        return new

    def info(self, url):
        return self.postprocess(self.info_for_id(self.id_from_url(URL(url))))


class Flickr(DataProvider):
    def __init__(self):
        self.api = flickrapi.FlickrAPI(
            os.environ['FLICKR_KEY'], os.environ['FLICKR_SECRET'], format='parsed-json')
        self.licenses = {l['id']: l['url'] for l in
                         self.api.photos.licenses.getInfo()['licenses']['license']}

    def info_for_id(self, id_):
        # creator, date, place, gps, permission, comments (title '...')
        info = self.api.photos.getInfo(photo_id=id_)['photo']
        res = dict(
            creator=info['owner']['realname'] or info['owner']['username'],
            date=info['dates']['taken'],
            permission=self.licenses[info['license']],
            comments="title '%s'" % info['title']['_content'])
        if 'location' in info:
            place = self.api.places.getInfo(place_id=info['location']['woeid'])['place']
            res.update(
                place=place['name'],
                longitude=place['longitude'],
                latitude=place['latitude'])
        res.update(self.size(id_))
        return res

    def size(self, id_):
        biggest = {'width': 0}
        for size in self.api.photos.getSizes(photo_id=id_)['sizes']['size']:
            if size['label'] == 'Original':
                biggest = size
                break

            if int(size['width']) > biggest['width']:
                biggest = size
        return dict(source_url=biggest['source'], source=biggest['url'])

    def id_from_url(self, url):
        if not url.host().endswith('flickr.com'):
            return
        comps = url.path_segments()
        assert comps[0] == 'photos'
        return comps[2]


class Eol(DataProvider):
    """
    http://eol.org/api/data_objects/1.0/23049910.json

    {"dataObjects": [
        {
            "mimeType": "image/jpeg",
            "created": "2013-01-03T00:00:00Z",
            "license": "http://creativecommons.org/licenses/by/3.0/",
            "rightsHolder": "2013 Simon J. Tonge",
            "source": "http://calphotos.berkeley.edu/cgi/img_query?seq_num=432146&one=T",
            --> http://media.eol.org/data_objects/23049910
            "description": "Male",
            "eolMediaURL": "http://media.eol.org/content/2013/06/17/17/54173_orig.jpg",
            "location": "Chobe National Park (Botswana)",
            "agents": [
                {
                    "full_name": "Simon J. Tonge",
                    "homepage": "http://calphotos.berkeley.edu/cgi/photographer_query?where-name_full=Simon+J.+Tonge&one=T",
                    "role": "photographer"
                },
                {
                    "full_name": "CalPhotos",
                    "homepage": "http://calphotos.berkeley.edu/",
                    "role": "provider"
                }
            ],
            "references": [ ]
        }
    ]}
    """
    def info_for_id(self, id_):
        info = requests.get(
            'http://eol.org/api/data_objects/1.0/%s.json' % id_).json()['dataObjects'][0]
        agents = {a['role']: a['full_name'] for a in info['agents']}
        if 'eolMediaURL' in info:
            return {
                'creator': agents.get('photographer', agents.values()[0]),
                'date': info.get('created'),
                'permission': info['license'],
                'source': 'http://media.eol.org/data_objects/' + id_,
                'source_url': info['eolMediaURL'],
                'mime_type': info['mimeType'],
                'place': info.get('location'),
                'comments': info.get('description'),
            }

    def id_from_url(self, url):
        """
        http://media.eol.org/data_objects/23049910
        """
        if url.host() != 'eol.org':
            return
        comps = url.path_segments()
        if comps[0] != 'data_objects':
            return
        return comps[1]


class Wikimedia(DataProvider):
    filename_pattern = re.compile("(?P<fname>[a-zA-Z\-_,'\(\)%0-9]+\.(jpg|png|JPG))$")
    license_pattern = re.compile('CC\-(?P<clauses>[A-Z\-]+)\-(?P<version>[0-9\.]+)')
    license_map = {
        'PD-user': 'http://en.wikipedia.org/wiki/Public_domain',
        'PD 1923': 'http://en.wikipedia.org/wiki/Public_domain',
        'CC-PD-Mark': 'http://en.wikipedia.org/wiki/Public_domain',
        'PD other reasons': 'http://en.wikipedia.org/wiki/Public_domain',
        #'PD-user': 'http://en.wikipedia.org/wiki/Public_domain',
    }

    def info_for_id(self, id_):
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
                return BeautifulSoup(e.text).string

        info = et.fromstring(requests.get(
            'http://tools.wmflabs.org/magnus-toolserver/commonsapi.php',
            params=dict(image=id_)).content)
        res = dict(
            creator=text(info.find('file/author')),
            source=info.find('file/urls/description').text,
            source_url=info.find('file/urls/file').text,
            permission=info.find('licenses/license/name').text)
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

    def id_from_url(self, url):
        """http://commons.wikimedia.org/wiki/File:Alcelaphus_caama.jpg
        """
        if not url.host().endswith('wikimedia.org'):
            return
        comps = url.path_segments()
        if comps[0] == 'wiki':
            if 'File:' in comps[1]:
                return comps[1].split('File:')[1]
            else:
                return
        for comp in comps:
            m = self.filename_pattern.search(comp)
            if m:
                return m.group('fname')
        print(comps)


#
# TODO:
#
def get_info(img, providers):
    for field in ['source', 'source_url']:
        for provider in providers:
            if provider.id_from_url(URL(img[field])):
                return provider.info(img[field])


class Visitor(object):
    def __init__(self, data):
        self.data = data
        print(len(data))

    def __call__(self, index, row):
        if index == 0:
            self.cols = {col: i for i, col in enumerate(row)}
            return row
        key = '%s-%s' % (row[self.cols['taxa__id']], row[self.cols['tags']])
        row = [c.strip() for c in row]
        if key in self.data and self.data[key]['id']:
            info = self.data[key]
            for col in 'creator place permission comments'.split():
                if not row[self.cols[col]].strip() and info.get(col):
                    row[self.cols[col]] = info.get(col).strip().encode('utf8')

            for col in 'id date source source_url mime_type'.split():
                if info.get(col):
                    row[self.cols[col]] = info.get(col).encode('utf8')

            if 'latitude' in info and 'longitude' in info:
                row[self.cols['gps']] = '%s %s' % (info['latitude'], info['longitude'])
            return row


def update():
    data = jsonload(data_file('cn', 'images.json'), default={})
    providers = [Wikimedia(), Flickr(), Eol()]
    try:
        for img in csv_items('cn/images.csv'):
            key = '%s-%s' % (img['taxa__id'], img['tags'])
            if key in data:
                continue
            info = get_info(img, providers)
            if info:
                assert 'source_url' in info
                checksum = md5()
                res = requests.get(info['source_url'])
                checksum.update(res.content)
                checksum = checksum.hexdigest()
                info['id'] = checksum
                info.setdefault('mime_type', res.headers['content-type'])
                with open(data_file('cn', 'images', checksum), mode='wb') as fp:
                    fp.write(res.content)
                data[key] = info
    except:
        jsondump(data, data_file('cn', 'images.json'), indent=4)
        raise
    jsondump(data, data_file('cn', 'images.json'), indent=4)


def rewrite():
    visit('cn/images.csv', Visitor(jsonload(data_file('cn', 'images.json'))))


def mv():
    for info in jsonload(data_file('cn', 'images.json')).values():
        ext = 'png' if 'png' in info['mime_type'] else 'jpg'
        shutil.move(
            data_file('cn', 'images', info['id']),
            data_file('cn', 'images', '%s.%s' % (info['id'], ext)))


if __name__ == '__main__':
    #update()
    #rewrite()
    mv()
    #for provider in [Wikimedia(), Flickr(), Eol()]:
    #    if provider.id_from_url(URL(sys.argv[1])):
    #        print json.dumps(provider.info(sys.argv[1]), indent=4)

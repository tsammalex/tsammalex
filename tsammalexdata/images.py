import os
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
    """Given a URL of an accepted format, DataProviders can fetch metadata for an image.
    """
    @staticmethod
    def date(s):
        try:
            return str(parse(s)).split()[0]
        except:
            return

    def id_from_url(self, url, host, comps):
        """
        :return: An id to be passed into `info_for_id` or None, \
        if `url` is not recognized.
        """
        raise NotImplementedError()

    def info_for_id(self, id_):
        """
        :return: `dict` of metadata for an image.
        """
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
        """Interface method to be called when processing new images.

        This method ties together the DataProvider workflow.
        """
        url = URL(url)
        return self.postprocess(
            self.info_for_id(self.id_from_url(url, url.host(), url.path_segments())))


class Senckenberg(DataProvider):
    __example__ = (
        'http://www.westafricanplants.senckenberg.de/root/index.php?page_id=14&id=722#image=26800',
        {
            'creator': 'Ralf Biechele',
            'date': '2008-05-03',
            'place': 'Nigeria',
            'source': 'http://www.westafricanplants.senckenberg.de/root/index.php?page_id=14&id=722#image%3D26800',
            'source_url': 'http://www.westafricanplants.senckenberg.de/images/pictures/ficus_polita_img_04024_ralfbiechele_722_fc6e25.jpg',
            'permission': 'http://creativecommons.org/licenses/by-nc/4.0/',
        }
    )

    def id_from_url(self, url, host, comps):
        """This DataProvider recognizes URLs of the form

        http://www.africanplants.senckenberg.de/root/index.php?page_id=14&id=722#image=26

        Note that the URL fragment is necessary to determine the exact image referred to
        on the page, listing all images for a species.

        :param url: A URL.
        :return: `url` if recognized, else `None`.
        """
        if host.endswith('africanplants.senckenberg.de') \
                and url.fragment() \
                and len(comps) == 2 \
                and comps[0] == 'root' \
                and comps[1] in ['index.php']:
            return url

    def info_for_id(self, id_):
        """
        We expect and exploit markup of the following form:

           <img src="http://<host>/images/pictures/thumb_<img-filename>"
                title="PhotoID: 26800;
    Photographer: Ralf Biechele;
    Date: 2008-05-03 18:03:19;
    Location: Nigeria" />
        """
        photo_id = id_.fragment().split('=')[1]

        for img in BeautifulSoup(requests.get(id_).text).find_all('img'):
            if img.attrs.get('title', '').startswith('PhotoID: %s' % photo_id):
                res = {
                    'source': '%s' % id_,
                    'source_url': img.attrs['src'].replace('/thumb_', '/'),
                    'permission': 'http://creativecommons.org/licenses/by-nc/4.0/',
                }
                for k, v in [
                    l.split(': ', 1) for l in img.attrs['title'].split('; \n') if l
                ]:
                    if k == 'Date':
                        res['date'] = v.split(' ')[0]
                    elif k == 'Photographer':
                        res['creator'] = v
                    elif k == 'Location':
                        res['place'] = v
                return res
        return {}


class Zimbabweflora(DataProvider):
    __example__ = (
        'http://www.zimbabweflora.co.zw/speciesdata/image-display.php?species_id=100760&image_id=2',
        {
            'creator': 'P Ballings',
            'date': '2012-01-08',
            'gps': '-20.272510',
            'permission': 'http://creativecommons.org/licenses/by-nc/4.0/',
            'place': 'Zimbabwe, Great zimbabwe, Great enclosure',
            'source': 'http://www.zimbabweflora.co.zw/speciesdata/image-display.php?species_id=100760&image_id=2',
            'source_url': 'http://www.zimbabweflora.co.zw/speciesdata/images/10/100760-2.jpg',
        }
    )

    def id_from_url(self, url, host, comps):
        if host in ['www.zimbabweflora.co.zw', 'www.mozambiqueflora.com'] \
                and len(comps) == 2 \
                and comps[0] == 'speciesdata' \
                and comps[1] in ['species-record.php', 'image-display.php']:
            return url

    def info_for_id(self, id_):
        soup = BeautifulSoup(requests.get(id_).text)
        img = soup.find('img')
        if not img:
            return {}
        src = img.attrs['src']
        if not src.startswith('http:'):
            src = 'http://www.zimbabweflora.co.zw/speciesdata/' + src
        res = {
            'source': '%s' % id_,
            'source_url': src,
            'permission': 'http://creativecommons.org/licenses/by-nc/4.0/',
        }
        for table in soup.find_all('table'):
            if table.attrs['summary'] in [
                'Individual record details', 'Information about the photograph'
            ]:
                for tr in table.find_all('tr'):
                    k, v = [td.get_text(' ', strip=True) for td in tr.find_all('td')]
                    if v:
                        # Location Country Latitude Date Photographer
                        if k == 'Location:':
                            res['place'] = v
                        if k == 'Country:':
                            loc = res.get('place', '')
                            res['place'] = '%s%s%s' % (v, ', ' if loc else '', loc)
                        if k == 'Latitude:':
                            res['gps'] = v
                        if k == 'Date:' and v != 'No date':
                            res['date'] = parse(v).date().isoformat()
                        if k == 'Photographer:':
                            res['creator'] = v
        return res


class Flickr(DataProvider):
    __example__ = (
        'https://www.flickr.com/photos/damouns/78968973',
        {
            'comments': "title 'Bufo gutturalis'",
            'creator': 'Damien Boilley',
            'date': '2005-12-27',
            'permission': 'https://creativecommons.org/licenses/by/2.0/',
            'source': 'https://www.flickr.com/photos/damouns/78968973/sizes/o/',
            'source_url': 'https://farm1.staticflickr.com/39/78968973_f30ad8c62d_o.jpg',
        }
    )

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

    def id_from_url(self, url, host, comps):
        if host.endswith('flickr.com') and len(comps) > 2 and comps[0] == 'photos':
            return comps[2]


class Eol(DataProvider):
    __example__ = (
        'http://media.eol.org/data_objects/21916329',
        {
            'creator': 'Research Institute Senckenberg',
            'mime_type': 'image/jpeg',
            'permission': 'http://creativecommons.org/licenses/by-nc-sa/3.0/',
            'place': 'Burkina Faso',
            'source': 'http://media.eol.org/data_objects/21916329',
            'source_url': 'http://160.111.248.28/content/2012/08/24/08/75619_orig.jpg',
        }
    )

    def info_for_id(self, id_):
        try:
            info = requests.get(
                'http://eol.org/api/data_objects/1.0/%s.json' % id_).json()['dataObjects'][0]
        except:
            return {}
        agents = {a['role']: a['full_name'] for a in info['agents']}
        if 'eolMediaURL' in info:
            return {
                'creator': agents.get('photographer', list(agents.values())[0]),
                'date': info.get('created'),
                'permission': info['license'],
                'source': 'http://media.eol.org/data_objects/' + id_,
                'source_url': info['eolMediaURL'],
                'mime_type': info['mimeType'],
                'place': info.get('location'),
                'comments': info.get('description'),
            }

    def id_from_url(self, url, host, comps):
        """
        http://media.eol.org/data_objects/23049910
        """
        if host.endswith('eol.org') and len(comps) == 2 and comps[0] == 'data_objects':
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

    def id_from_url(self, url, host, comps):
        """http://commons.wikimedia.org/wiki/File:Alcelaphus_caama.jpg
        """
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

PROVIDERS = [Wikimedia(), Flickr(), Eol(), Zimbabweflora(), Senckenberg()]


class Visitor(object):
    def __init__(self, data):
        self.data = data
        print(len(data))

    def __call__(self, index, row):
        if index == 0:
            self.cols = {col: i for i, col in enumerate(row)}
            return row
        #if index == 1:
        #    print(self.cols)
        #if len(row) < len(self.cols):
        #    print(row)
        #return row
        if len(row) < 3:
            print(row)
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
    def get_info(img):
        for field in ['source', 'source_url', 'id']:
            for provider in PROVIDERS:
                url = URL(img[field])
                if provider.id_from_url(url, url.host(), url.path_segments()):
                    return provider.info(img[field])

    data = jsonload(data_file('cn', 'images.json'), default={})
    try:
        info = None
        for img in csv_items('cn/images.csv'):
            key = '%s-%s' % (img['taxa__id'], img['tags'])
            if key in data:
                print('+++', img['id'] or img['source'], data[key]['source'])
                continue
            info = get_info(img)
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
                print(info)
            #else:
            #    print('---', img)
    except:
        print('----->')
        print(img)
        if info:
            print(info)
        jsondump(data, data_file('cn', 'images.json'), indent=4)
        raise
    jsondump(data, data_file('cn', 'images.json'), indent=4)


def rewrite():
    visit('cn/images.csv', Visitor(jsonload(data_file('cn', 'images.json'))))


def mv():
    for info in jsonload(data_file('cn', 'images.json')).values():
        ext = 'png' if 'png' in info['mime_type'] else 'jpg'
        if os.path.exists(data_file('cn', 'images', info['id'])):
            shutil.move(
                data_file('cn', 'images', info['id']),
                data_file('cn', 'images', '%s.%s' % (info['id'], ext)))


class Deduplicator(object):
    def __init__(self, data):
        self.data = data
        self.count = 0

    def __call__(self, index, row):
        if index == 0 or row[0] not in self.data:
            return row
        self.count += 1


def dedup():
    existing = [i['id'] for i in csv_items('images.csv') if 'edmond' in i['source_url']]
    d = Deduplicator(existing)
    visit('cn/images.csv', d)
    print(d.count)


def check():
    count = 0
    files = {n.split('.')[0]: n for n in os.listdir(data_file('cn/images'))}
    existing = [i['id'] for i in csv_items('cn/images.csv') if 'edmond' in i['source_url']]
    #existing = file_urls(data_file('Edmond.xml'))
    for id, fname in files.items():
        if id in existing:
            count += 1
            shutil.move(
                data_file('cn', 'images', fname), data_file('cn', 'uploaded', fname))
    print(count)


class RemoveUploaded(object):
    def __init__(self, data):
        self.data = data

    def __call__(self, index, row):
        if len(row) < 3:
            return row
        if index > 0 and (row[1], row[2]) not in self.data:
            return row


def do_check(fname):
    existing = {(i['taxa__id'], i['tags']): i for i in
                csv_items('images.csv') if 'edmond' in i['source_url']}
    visit(fname, RemoveUploaded(existing))
    #c = 0
    #for i, row in enumerate(csv_items(fname)):
    #    if (row['taxa__id'], row['tags']) in existing:
    #        if 0: #row['id'] != existing[(row['taxa__id'], row['tags'])]['source']:
    #            print(row)
    #            print(existing[(row['taxa__id'], row['tags'])])
    #        else:
    #            c += 1
    #print('%s of %s' % (c, i))


class Selector(object):
    def __call__(self, index, row):
        if index == 0:
            self.cols = {col: i for i, col in enumerate(row)}
            return row
        if 'edmond.' in row[self.cols['source_url']]:
            return row


def select():
    shutil.copy(data_file('cn', 'images.csv'), data_file('cn', 'staged_images.csv'))
    visit('cn/staged_images.csv', Selector())
    print(len(open(data_file('cn', 'staged_images.csv')).read().split('\n')) - 1)


class CN(object):
    def __call__(self, index, row):
        if index == 0:
            return row
        if not os.path.exists(data_file('cn', 'files', row[0])):
            return row
        if not row[9]:
            return row
        path = data_file('cn', 'files', row[0])
        checksum = md5()
        with open(path, 'rb') as fp:
            checksum.update(fp.read())
        row[0] = checksum.hexdigest()

        shutil.move(path, data_file('cn', 'images', row[0] + '.jpg'))
        return row


"""
(clld)robert@astroman:~/venvs/clld/data/tsammalex-data/tsammalexdata$ python images.py check cn/images_newLS150310.csv
1063 of 1169
(clld)robert@astroman:~/venvs/clld/data/tsammalex-data/tsammalexdata$ python images.py check cn/images_new_150304_NJ.csv
881 of 1039
(clld)robert@astroman:~/venvs/clld/data/tsammalex-data/tsammalexdata$ python images.py check cn/images_newCN150309final.csv
1219 of 1385

- download images and metadata
    python images.py update
- rewrite cn/images.csv with metadata from cn/images.json:
    python images.py rewrite
- upload images from cn/images to edmond
- run
    python edmond.py cn/images.csv
  to add edmond source urls
- move images to uploaded
- create staging file
    python images.py stage
- append rows from staging file to official images.csv (by hand)
- run nosetests
- remove rows from cn/images.csv
    python images.py purge
"""


if __name__ == '__main__':
    import sys
    #visit(sys.argv[1], CN())
    #sys.exit(0)

    cmd = sys.argv[1]
    if cmd == 'stage':
        check()
        select()
    elif cmd == 'purge':
        dedup()
    elif cmd == 'check':
        do_check(sys.argv[2])
    elif cmd == 'update':
        update()
    elif cmd == 'rewrite':
        rewrite()
    elif cmd == 'test':
        for provider in PROVIDERS:
            if hasattr(provider, '__example__'):
                url, info = provider.__example__
                res = provider.info(url)
                if res != info:
                    print('ERROR:')
                    for d in [res, info]:
                        for k in sorted(d.keys()):
                            print(k, d[k])
                else:
                    print('OK')
    else:
        raise ValueError(cmd)
    #update()
    #rewrite()
    #mv()
    #for provider in [Wikimedia(), Flickr(), Eol()]:
    #    if provider.id_from_url(URL(sys.argv[1])):
    #        print json.dumps(provider.info(sys.argv[1]), indent=4)

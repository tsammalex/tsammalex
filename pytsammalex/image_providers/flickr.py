# coding: utf8
from __future__ import unicode_literals, print_function, division
import os

from flickrapi import FlickrAPI
from clldutils.misc import cached_property

from pytsammalex.image_providers.base import ImageProvider


class Flickr(ImageProvider):
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

    def __init__(self, *args):
        ImageProvider.__init__(self, *args)
        self.api = FlickrAPI(
            os.environ.get('FLICKR_KEY', ''),
            os.environ.get('FLICKR_SECRET', ''),
            format='parsed-json')

    def identify(self, item):
        url, host, comps = self.url_parts(item.id)
        if host.endswith('flickr.com') and len(comps) > 2 and comps[0] == 'photos':
            return comps[2]

    @cached_property()
    def licenses(self):
        return {l['id']: l['url'] for l in
                self.api.photos.licenses.getInfo()['licenses']['license']}

    def metadata(self, item):
        id_ = self.identify(item)
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

            if int(size['width']) > int(biggest['width']):
                biggest = size
        return dict(source_url=biggest['source'], source=biggest['url'])

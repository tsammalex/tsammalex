# coding: utf8
from __future__ import unicode_literals, print_function, division

from pytsammalex.image_providers.base import ImageProvider


class Senckenberg(ImageProvider):
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

    def identify(self, item):
        """This DataProvider recognizes URLs of the form

        http://www.africanplants.senckenberg.de/root/index.php?page_id=14&id=722#image=26

        Note that the URL fragment is necessary to determine the exact image referred to
        on the page, listing all images for a species.

        :param url: A URL.
        :return: `url` if recognized, else `None`.
        """
        url, host, comps = self.url_parts(item.id)
        if host.endswith('africanplants.senckenberg.de') \
                and url.fragment() \
                and len(comps) == 2 \
                and comps[0] == 'root' \
                and comps[1] in ['index.php']:
            return url

    def metadata(self, item):
        """
        We expect and exploit markup of the following form:

           <img src="http://<host>/images/pictures/thumb_<img-filename>"
                title="PhotoID: 26800;
    Photographer: Ralf Biechele;
    Date: 2008-05-03 18:03:19;
    Location: Nigeria" />
        """
        id_ = self.identify(item)
        photo_id = id_.fragment().split('=')[1]

        for img in self.bs(self.get(id_).text).find_all('img'):
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

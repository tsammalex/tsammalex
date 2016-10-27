# coding: utf8
from __future__ import unicode_literals, print_function, division

from pytsammalex.images import ImageProvider


class Eol(ImageProvider):
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

    def identify(self, item):
        """
        http://media.eol.org/data_objects/23049910
        """
        url, host, comps = ImageProvider.url_parts(item)
        if host.endswith('eol.org') and len(comps) == 2 and comps[0] == 'data_objects':
            return comps[1]

    def metadata(self, item):
        id_ = self.identify(item)
        try:
            info = self.get(
                'http://eol.org/api/data_objects/1.0/%s.json' % id_
            ).json()['dataObjects'][0]
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

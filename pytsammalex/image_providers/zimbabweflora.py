# coding: utf8
from __future__ import unicode_literals, print_function, division

from pytsammalex.images import ImageProvider


class Zimbabweflora(ImageProvider):
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

    def identify(self, item):
        url, host, comps = ImageProvider.url_parts(item)
        if host in ['www.zimbabweflora.co.zw', 'www.mozambiqueflora.com'] \
                and len(comps) == 2 \
                and comps[0] == 'speciesdata' \
                and comps[1] in ['species-record.php', 'image-display.php']:
            return url

    def metadata(self, item):
        id_ = self.identify(item)
        soup = self.bs(self.get(id_).text)
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
                            res['gps'] = v + ' 0.0'
                        if k == 'Date:' and v != 'No date':
                            res['date'] = v
                        if k == 'Photographer:':
                            res['creator'] = v
        return res

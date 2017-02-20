from __future__ import print_function, unicode_literals, absolute_import, division

from Levenshtein import distance

from pytsammalex.data_providers.base import DataProvider


class EOL(DataProvider):
    def _api(self, name, id=None, **kw):
        path = '1.0'
        if id:
            path += '/%s' % id
        url = 'http://eol.org/api/%s/%s.json' % (name, path)
        try:
            return self.get(url, type_='json', **kw)
        except ValueError:  # pragma: no cover
            return {}

    def identify(self, name):
        res = self._api('search', q=name, page=1, exact='false')
        if res.get('results'):
            for result in res['results']:
                if result['title'] == name:
                    break  # pragma: no cover
            else:
                result = res['results'][0]
            return result['id']

    def get_taxon_concept(self, data):
        if data.get('taxonConcepts'):
            # augment the data with complete classification info for one taxonomy:
            for tc in data['taxonConcepts']:
                if tc['nameAccordingTo'].startswith('Species 2000'):
                    # this is our preferred taxonomy ...
                    return tc
            # ... but any will do :)
            return data['taxonConcepts'][0]  # pragma: no cover

    def metadata(self, id):
        """Extract classification and synonym/common name data from EOL for a given taxon.

        :param id: EOL id of a taxon.
        :return: dict with information.
        """
        kw = dict(
            images=0,
            videos=0,
            sounds=0,
            maps=0,
            text=0,
            iucn='true',
            subjects='overview',
            licenses='all',
            details='true',
            common_names='true',
            synonyms='true',
            references='false',
            vetted=0)
        data = self._api('pages', id, **kw)
        if isinstance(data, list):
            return {}  # pragma: no cover
        tc = self.get_taxon_concept(data)
        if tc:
            taxonomy = self._api('hierarchy_entries', tc['identifier'])
            data.update(ancestors=taxonomy['ancestors'])
        return data

    def update(self, taxon, data):
        for ancestor in data.get('ancestors', []):
            if 'taxonRank' not in ancestor:
                continue  # pragma: no cover
            for k in 'kingdom phylum class order family genus'.split():
                if ancestor['taxonRank'] == k:
                    taxon[k] = ancestor['scientificName'].split()[0]
                    break
        tc = self.get_taxon_concept(data)
        if tc and 'taxonRank' in tc:
            taxon['taxonRank'] = tc['taxonRank'].lower()
        for vn in data.get('vernacularNames', []):
            if vn.get('language') == 'en' and vn.get('eol_preferred'):
                taxon['english_name'] = vn['vernacularName']
                break

    def search_fuzzy(self, name):  # pragma: no cover
        """
        http://eol.org/search?q=Ammodaucus+leucothricus&search=Go
        <div id='main'>
        Did you mean: <a href="/search?q=ammodaucus+leucotrichus">Ammodaucus leucotrichus</a>, <a href="/search?q=ammodaucus+leucotrichus+coss.">Ammodaucus leucotrichus coss.</a>, <a href="/search?q=oreocereus+leucotrichus">Oreocereus leucotrichus</a>, <a href="/search?q=acrolophus+leucotricha">Acrolophus leucotricha</a>, <a href="/search?q=ammodiscus+catinus">Ammodiscus catinus</a>, <a href="/search?q=ammodiscus+excertus">Ammodiscus excertus</a> ?
        <div class='filtered_search'>
        """
        res = self.get('http://eol.org/search', params=dict(q=name, search='Go'))
        maindiv = self.bs(res.text).find('div', id='main')
        candidate = None
        if maindiv:
            for a in maindiv.find_all('a'):
                if a['href'].startswith('/search?q='):
                    if distance(name.decode('utf8'), a.text.strip()) < 3:
                        candidate = a.text
                        #print(a.text)
        if candidate:
            print(name.decode('utf8'), '->', candidate)
        return candidate

from __future__ import print_function, unicode_literals, absolute_import, division
import sys

import requests
from bs4 import BeautifulSoup
from Levenshtein import distance

from tsammalexdata.util import data_file, jsonload, jsondump, csv_items, DataProvider


def search_fuzzy(name):
    """
    http://eol.org/search?q=Ammodaucus+leucothricus&search=Go
<div id='main'>
Did you mean: <a href="/search?q=ammodaucus+leucotrichus">Ammodaucus leucotrichus</a>, <a href="/search?q=ammodaucus+leucotrichus+coss.">Ammodaucus leucotrichus coss.</a>, <a href="/search?q=oreocereus+leucotrichus">Oreocereus leucotrichus</a>, <a href="/search?q=acrolophus+leucotricha">Acrolophus leucotricha</a>, <a href="/search?q=ammodiscus+catinus">Ammodiscus catinus</a>, <a href="/search?q=ammodiscus+excertus">Ammodiscus excertus</a> ?
<div class='filtered_search'>
    """
    res = requests.get('http://eol.org/search', params=dict(q=name, search='Go'))
    maindiv = BeautifulSoup(res.text).find('div', id='main')
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


class EOL(DataProvider):
    host = 'eol.org'

    def _path(self, name, id=None):
        path = '1.0'
        if id:
            path += '/%s' % id
        return 'api/%s/%s.json' % (name, path)

    def _api(self, name, id=None, **kw):
        try:
            return self.get(self._path(name, id), **kw)
        except ValueError:
            return {}

    def get_id(self, name):
        res = self._api('search', q=name, page=1, exact='false')
        if res.get('results'):
            for result in res['results']:
                if result['title'] == name:
                    return result['id']
            return res['results'][0]['id']

    def get_info(self, id):
        """Extract classification and synonym/common name data from EOL for a given species.

        :param id: EOL id of a species.
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
            return {}
        if data.get('taxonConcepts'):
            # augment the data with complete classification info for one taxonomy:
            for tc in data['taxonConcepts']:
                if tc['nameAccordingTo'].startswith('Species 2000'):
                    # this is our preferred taxonomy ...
                    break
            else:
                tc = data['taxonConcepts'][0]
                # ... but any will do :)
            taxonomy = self._api('hierarchy_entries', tc['identifier'])
            data.update(ancestors=taxonomy['ancestors'])
        return data

    def update(self, species, data):
        for ancestor in data.get('ancestors', []):
            if 'taxonRank' not in ancestor:
                continue
            for k in 'kingdom order family genus'.split():
                if ancestor['taxonRank'] == k:
                    species[k] = ancestor['scientificName'].split()[0]
                    break


if __name__ == '__main__':
    args = sys.argv[1:]
    if args:
        search_fuzzy(args[0])
    else:
        fname = data_file('external', 'eol.json')
        species = jsonload(fname)

        eol = EOL()
        for item in csv_items('species.csv'):
            if item['id'] not in species:
                try:
                    species[item['id']] = eol.get_info(item['eol_id'] or None)
                except:
                    # we'll have to try again next time!
                    print('missing:', item['id'])
                    pass

        jsondump(species, fname)

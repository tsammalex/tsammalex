from __future__ import print_function, unicode_literals, absolute_import, division

import requests
from purl import URL

from tsammalexdata.util import data_file, jsonload, jsondump, csv_items


def eol_api(name, id=None, **kw):
    """Access the EOL API.

    .. seealso:: http://eol.org/api

    :param name: Name of the API call.
    :param id: EOL object identifier or None.
    :param kw: URL query params.
    :return: decoded JSON response.
    """
    path = '1.0'
    if name != 'search':
        path += '/%s' % id
    url = URL('http://eol.org/api/%s/%s.json' % (name, path)).query_params(kw)
    try:
        return requests.get(url).json()
    except ValueError:
        print(name, id)
        return {}


def get_eol_id(name):
    res = eol_api('search', q=name, page=1, exact='false')
    if res.get('results'):
        return res['results'][0]['id']


def eol(id):
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
    data = eol_api('pages', id, **kw)
    if isinstance(data, list):
        print(data)
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
        taxonomy = eol_api('hierarchy_entries', tc['identifier'])
        data.update(ancestors=taxonomy['ancestors'])
    return data


if __name__ == '__main__':
    fname = data_file('external', 'eol.json')
    species = jsonload(fname)

    for item in csv_items('species.csv'):
        if item['id'] not in species:
            try:
                species[item['id']] = eol(item['eol_id'] or None)
                print(item['id'])
            except:
                # we'll have to try again next time!
                pass

    jsondump(species, fname)

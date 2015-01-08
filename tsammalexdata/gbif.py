from __future__ import print_function, unicode_literals
import os

import requests

from tsammalexdata.util import data_file, csv_items, jsondump, jsonload


BASE_URL = 'http://api.gbif.org/v1'


def api(path, **params):
    return requests.get('/'.join([BASE_URL, path]), params=params).json()


def get_occurrences(species):
    kw = dict(
        taxonKey=api('species/match', name=species)['speciesKey'],
        basisOfRecord='HUMAN_OBSERVATION',
        hasCoordinate='true',
        limit=100)
    return api('occurrence/search', **kw)


def save_occurrences(sid, sname):
    out = data_file('external', 'gbif', '%s.json' % sid)
    if not os.path.exists(out):
        try:
            res = get_occurrences(sname)
            jsondump(res, out)
            print('%s: %s occurrences' % (sname, min([res['count'], res['limit']])))
        except:
            # we'll have to try again next time!
            res = None
    else:
        try:
            res = jsonload(out)
        except:
            os.remove(out)
            res = None
    return res


if __name__ == '__main__':
    for item in csv_items('species.csv'):
        save_occurrences(item['id'], item['scientific_name'])

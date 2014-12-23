from __future__ import print_function, unicode_literals
import os

import requests

from tsammalexdata.util import data_file, csv_items, jsondump


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


if __name__ == '__main__':
    for item in csv_items('species.csv'):
        out = data_file('external', 'gbif', '%s.json' % item['id'])
        if not os.path.exists(out):
            try:
                res = get_occurrences(item['scientific_name'])
                jsondump(res, out)
                print('%s: %s occurrences' %
                      (item['scientific_name'], min([res['count'], res['limit']])))
            except:
                # we'll have to try again next time!
                pass

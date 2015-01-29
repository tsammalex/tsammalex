from __future__ import print_function, unicode_literals
import os

from tsammalexdata.util import data_file, csv_items, jsondump, jsonload, DataProvider


BASE_URL = 'http://api.gbif.org/v1'


class GBIF(DataProvider):
    host = 'api.gbif.org'

    def get_id(self, name):
        res = self.get('v1/species/match', name=name)
        return res[res['rank'].lower() + 'Key']

    def get_info(self, id):
        kw = dict(
            taxonKey=id,
            basisOfRecord='HUMAN_OBSERVATION',
            hasCoordinate='true',
            limit=100)
        return self.get('v1/occurrence/search', **kw)

    def update_species(self, species):
        #
        # TODO: update classification!
        #
        pass


def save_occurrences(sid, sname):
    api = GBIF()
    out = data_file('external', 'gbif', '%s.json' % sid)
    if not os.path.exists(out):
        try:
            res = api.get_info(api.get_id(sname))
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

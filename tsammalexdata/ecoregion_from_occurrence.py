from __future__ import print_function, unicode_literals
import os
from collections import OrderedDict
from io import open

try:
    from shapely.geometry import shape, Point
    from shapely.geos import PredicateError
except ImportError:
    raise

from tsammalexdata.util import data_file, jsonload


INVALID_ECO_CODES = {'AA0803', 'Lake', 'AT1202', 'IM1303', 'AA0803'}


def main():
    res = OrderedDict()
    ecoregions = [
        (er['properties']['eco_code'], shape(er['geometry']))
        for er in jsonload(data_file('ecoregions.json'))['features']
        if er['geometry'] and er['properties']['eco_code'] not in INVALID_ECO_CODES]
    for fname in os.listdir(data_file('external', 'gbif')):
        res[fname.split('.')[0]] = ';'.join(sorted(set(match(
            jsonload(data_file('external', 'gbif', fname))['results'], ecoregions))))

    with open(data_file('ecoregions_from_occurrences.csv'), 'w', encoding='utf8') as fp:
        for item in res.items():
            print('%s: %s' % item)
            fp.write('%s,%s\n' % item)


def match(occurrences, ecoregions):
    for oc in occurrences:
        point = Point(oc['decimalLongitude'], oc['decimalLatitude'])
        for eco_code, er in ecoregions:
            try:
                if er.contains(point):
                    yield eco_code
            except PredicateError:
                print('--error--: ', eco_code)
                pass


if __name__ == '__main__':
    main()

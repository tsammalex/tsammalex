from __future__ import print_function, unicode_literals
import os
from io import open

from shapely.geometry import shape, Point
from shapely.geos import PredicateError

from tsammalexdata.util import data_file, jsonload, unique


INVALID_ECO_CODES = {'AA0803', 'Lake', 'AT1202', 'IM1303', 'AA0803'}
DATA_FILE = data_file('distribution.csv')


def format_ids(iterable):
    return ';'.join(unique(iterable))


def main():
    res = {}
    with open(DATA_FILE, encoding='utf8') as fp:
        for line in fp.read().split('\n'):
            if line:
                cols = line.split(',')
                res[cols[0]] = cols[1:]

    ecoregions = [
        (er['properties']['eco_code'], shape(er['geometry']))
        for er in jsonload(data_file('ecoregions.json'))['features']
        if er['geometry'] and er['properties']['eco_code'] not in INVALID_ECO_CODES]

    for fname in os.listdir(data_file('external', 'gbif')):
        sid = fname.split('.')[0]
        v = res.get(sid, ['', ''])
        if len(v) == 1:
            v.append('')
        if not v[0] or not v[1]:
            occurrences = jsonload(
                data_file('external', 'gbif', fname)).get('results', [])
        if not v[0]:
            v[0] = format_ids(match(occurrences, ecoregions))
        if not v[1]:
            v[1] = format_ids(r.get('countryCode') for r in occurrences)
        res[sid] = v

    with open(DATA_FILE, 'w', encoding='utf8') as fp:
        for key in sorted(res.keys()):
            fp.write('%s,%s\r\n' % (key, ','.join(res[key])))


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

from __future__ import print_function, unicode_literals

from tqdm import tqdm
from shapely.geometry import shape, Point
from shapely.geos import PredicateError, TopologicalError
from clldutils import jsonlib

from pytsammalex.models import CsvData, Distribution
from pytsammalex.util import data_file

INVALID_ECO_CODES = {'AA0803', 'Lake', 'AT1202', 'IM1303', 'AA0803'}


def update(repos, verbose=True):
    ecoregions = [
        (er['properties']['eco_code'], shape(er['geometry']))
        for er in jsonlib.load(data_file('ecoregions.json', repos=repos))['features']
        if er['geometry'] and er['properties']['eco_code'] not in INVALID_ECO_CODES]

    with CsvData('distribution', repos=repos) as data:
        res = {i.id: i for i in data.items}

        occurrence_data = list(data_file('external', 'gbif', repos=repos).glob('*.json'))
        if verbose:  # pragma: no cover
            occurrence_data = tqdm(occurrence_data)
        for fname in occurrence_data:
            sid = fname.stem
            d = res.get(sid, Distribution(sid, '', ''))
            if not d.countries__ids or not d.ecoregions__ids:
                occurrences = jsonlib.load(fname).get('results', [])
                if not d.ecoregions__ids:
                    d.ecoregions__ids = list(match(occurrences, ecoregions))
                if not d.countries__ids:
                    d.countries__ids = list(r.get('countryCode') for r in occurrences)
            res[sid] = d
            data.items = [res[key] for key in sorted(res.keys())]


def match(occurrences, ecoregions):
    for oc in occurrences:
        point = Point(oc['decimalLongitude'], oc['decimalLatitude'])
        for eco_code, er in ecoregions:
            try:
                if er.contains(point):
                    yield eco_code
            except (PredicateError, TopologicalError):  # pragma: no cover
                print('--error--: ', eco_code)
                pass

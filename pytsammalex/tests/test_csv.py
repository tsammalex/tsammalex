from __future__ import unicode_literals, print_function, division
import re
from collections import OrderedDict
import logging
logging.getLogger('pycountry.db').setLevel(logging.INFO)

from pycountry import countries
from clldutils import jsonlib
import attr

from pytsammalex.util import data_file, REPOS
from pytsammalex import models


SUCCESS = True
BIB_ID_PATTERN = re.compile('@[a-zA-Z]+\{(?P<id>[^,]+),')
CSV = [
    'audios',
    'categories',
    'contributors',
    'distribution',
    'habitats',
    'images',
    'languages',
    'lineages',
    'names',
    'taxa',
    'uses',
]


def error(msg, name, line=''):  # pragma: no cover
    global SUCCESS
    SUCCESS = False
    if line:
        line = ':%s' % line
    print('ERROR:%s%s: %s' % (name, line, msg))


def test():
    if not REPOS.exists():
        return
    data = {
        n: OrderedDict([(item.id, item) for item in models.CsvData(n, on_error=error)])
        for n in CSV}
    data['ecoregions'] = {}
    for ecoregion in jsonlib.load(data_file('ecoregions.json'))['features']:
        data['ecoregions'][ecoregion['properties']['eco_code']] = ecoregion

    data['refs'] = {}
    with data_file('sources.bib').open(encoding='utf8') as fp:
        for line in fp:
            match = BIB_ID_PATTERN.match(line.strip())
            if match:
                data['refs'][match.group('id')] = 1

    data['countries'] = {country.alpha2: country for country in countries}

    for name in ['names', 'taxa']:
        for line, item in enumerate(data[name].values()):
            for ref in item.refs__ids:
                if '[' in ref:
                    source_id, pages = ref.split('[', 1)
                    if not pages.endswith(']'):  # pragma: no cover
                        error('invalid reference %s' % (ref,), name, line + 2)
                else:
                    source_id = ref
                if source_id not in data['refs']:  # pragma: no cover
                    error('invalid id referenced: %s' % (source_id,), name, line + 2)

    for name, model in [(n, getattr(models, n.capitalize())) for n in CSV]:
        for line, item in enumerate(data[name].values()):
            for col in [f.name for f in attr.fields(model)]:
                if '__' in col:
                    ref, cardinality = col.split('__', 1)
                    #if ref not in data:
                    #    continue
                    ids = getattr(item, col)
                    if cardinality == 'id':
                        assert not isinstance(ids, list)
                        ids = [ids]
                    for v in ids:
                        if ref not in data:
                            raise ValueError(ref)  # pragma: no cover
                        if ref == 'refs' and '[' in v:
                            v = v.split('[')[0]
                        if v not in data[ref]:  # pragma: no cover
                            error(
                                'invalid %s id referenced: %s' % (ref, v), name, line + 2)

    if not SUCCESS:  # pragma: no cover
        raise ValueError('integrity checks failed!')

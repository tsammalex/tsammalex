import os
import re
import io
import logging
logging.getLogger('pycountry.db').setLevel(logging.INFO)

from pycountry import countries

from tsammalexdata.util import jsonload, data_file, csv_items, split_ids


SUCCESS = True
BIB_ID_PATTERN = re.compile('@[a-zA-Z]+\{(?P<id>[^,]+),')
CSV = [
    'audios',
    'categories',
    'contributors',
    'habitats',
    'images',
    'languages',
    'lineages',
    'names',
    'taxa',
    'uses',
]


def error(msg, name, line=''):
    global SUCCESS
    SUCCESS = False
    if line:
        line = ':%s' % line
    print('ERROR:%s%s: %s' % (name, line, msg))


def read_csv(name, unique='id'):
    uniquevalues = set()
    rows = []
    for line, row in enumerate(csv_items(name)):
        line += 2
        if unique:
            if unique not in row:
                error('unique key missing: %s' % unique, name, line)
                continue
            if row[unique] in uniquevalues:
                error('non-unique id: %s' % row[unique], name, line)
            uniquevalues.add(row[unique])
        rows.append((line, row))
    return rows


def test():
    data = {n: read_csv(n) for n in CSV}
    ids = {n: {r[1]['id'] for r in rows} for n, rows in data.items()}

    ids['ecoregions'] = set()
    for ecoregion in jsonload(data_file('ecoregions.json'))['features']:
        ids['ecoregions'].add(ecoregion['properties']['eco_code'])

    ids['sources'] = set()
    with io.open(data_file('sources.bib'), encoding='utf8') as fp:
        for line in fp:
            match = BIB_ID_PATTERN.match(line.strip())
            if match:
                ids['sources'].add(match.group('id'))

    ids['countries'] = set([country.alpha2 for country in countries])

    def check_ref(name, line, item):
        for ref in item['refs__ids'].split(';'):
            if ref:
                if '[' in ref:
                    source_id, pages = ref.split('[', 1)
                    if not pages.endswith(']'):
                        error('invalid reference %s' % (ref,), name, line)
                else:
                    source_id = ref
                if source_id not in ids['sources']:
                    error('invalid sources id referenced: %s' % (source_id,), name, line)

    for name in ['names', 'taxa']:
        for line, item in data[name]:
            check_ref(name, line, item)

    for name, items in data.items():
        for line, item in items:
            for col in item.keys():
                if '__' in col:
                    ref, card = col.split('__', 1)
                    if ref not in ids:
                        continue
                    for v in split_ids(item[col]):
                        if v not in ids[ref]:
                            error('invalid %s id referenced: %s' % (ref, v), name, line)

    if not SUCCESS:
        raise ValueError('integrity checks failed!')

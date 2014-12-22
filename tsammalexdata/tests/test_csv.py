import os
import re
import io

from pycountry import countries

from tsammalexdata.util import jsonload, data_file, csv_items


SUCCESS = True
ID_SEP_PATTERN = re.compile('\.|,|;')
BIB_ID_PATTERN = re.compile('@[a-zA-Z]+\{(?P<id>[^,]+),')


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
            if row[unique] in uniquevalues:
                error('non-unique id: %s' % row[unique], name, line)
            uniquevalues.add(row[unique])
        rows.append((line, row))
    return rows


def test():
    data = {n[:-4]: read_csv(n) for n in os.listdir(data_file()) if n.endswith('.csv')}
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

    for name in ['names', 'species']:    
        for line, item in data[name]:
            check_ref(name, line, item)

    for name, items in data.items():
        for line, item in items:
            for col in item.keys():
                if '__' in col:
                    ref, card = col.split('__', 1)
                    if ref not in ids:
                        continue
                    for v in ID_SEP_PATTERN.split(item[col]):
                        v = v.strip()
                        if v and v not in ids[ref]:
                            error('invalid %s id referenced: %s' % (ref, v), name, line)

    if not SUCCESS:
        raise ValueError('integrity checks failed!')

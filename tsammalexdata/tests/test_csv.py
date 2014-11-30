import os
import csv

import tsammalexdata


SUCCESS = True


def error(msg, name, line=''):
    global SUCCESS
    SUCCESS = False
    if line:
        line = ':%s' % line
    print('ERROR:%s%s: %s' % (name, line, msg))


def data_file(name):
    return os.path.join(os.path.dirname(tsammalexdata.__file__), 'data', name)


def read_csv(name, unique='id'):
    uniquevalues = set()
    rows = []
    with open(data_file(name + '.csv')) as csvfile:
        for line, row in enumerate(csv.DictReader(csvfile)):
            line += 2
            if unique:
                if row[unique] in uniquevalues:
                    error('non-unique id: %s' % row[unique], name, line)
                uniquevalues.add(row[unique])
            rows.append((line, row))
    return rows


def test():
    species = {s[1]['id']: 1 for s in read_csv('species')}
    for line, img in read_csv('images'):
        if img['species_id'] not in species:
            error('invalid species id referenced: %s' % img['species_id'], 'images', line)
    for line, lang in read_csv('languages'):
        pass
    if not SUCCESS:
        raise ValueError('integrity checks failed!')

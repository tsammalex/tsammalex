import os
import sys
import json
import csv
import shutil

import tsammalexdata


PY3 = sys.version_info[0] == 3


def data_file(*comps):
    return os.path.join(os.path.dirname(tsammalexdata.__file__), 'data', *comps)


def csv_items(name, lineno=False):
    items = []
    with open(data_file(name)) as csvfile:
        for item in csv.DictReader(csvfile):
            items.append(item)
    return items


def visit(name, visitor=None):
    """Utility function to rewrite rows in csv files.

    :param name: Name of the csv file to operate on.
    :param visitor: A callable that takes a row as input and returns a (modified) row or\
    None to filter out the row.
    """
    if visitor is None:
        visitor = lambda r: r
    tmp = data_file('.' + name)
    with open(data_file(name), 'rb') as source:
        with open(tmp, 'wb') as target:
            writer = csv.writer(target)
            for i, row in enumerate(csv.reader(source)):
                row = visitor(i, row)
                if row:
                    writer.writerow(row)
    shutil.move(tmp, data_file(name))


def jsondump(obj, path):
    """python 2 + 3 compatible version of json.dump.

    :param obj: The object to be dumped.
    :param path: The path of the JSON file to be written.
    """
    kw = dict(mode='w')
    if PY3:  # pragma: no cover
        kw['encoding'] = 'utf8'
    with open(path, **kw) as fp:
        return json.dump(obj, fp)


def jsonload(path):
    """python 2 + 3 compatible version of json.load.

    :return: The python object read from path.
    """
    kw = {}
    if PY3:  # pragma: no cover
        kw['encoding'] = 'utf8'
    with open(path, **kw) as fp:
        return json.load(fp)

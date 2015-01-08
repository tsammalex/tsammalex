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
    data = data_file(name)
    if os.path.isdir(data):
        fnames = [os.path.join(data, fname) for fname in os.listdir(data) if fname.endswith('.csv')]
    elif os.path.isfile(data):
        fnames = [data]
    elif os.path.isfile(data + '.csv'):
        fnames = [data + '.csv']
    else:
        raise ValueError(name)

    items = []
    for fname in fnames:
        with open(data_file(fname)) as csvfile:
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
    fname = data_file(name)
    tmp = os.path.join(os.path.dirname(fname), '.' + os.path.basename(fname))
    with open(fname, 'rb') as source:
        with open(tmp, 'wb') as target:
            writer = csv.writer(target)
            for i, row in enumerate(csv.reader(source)):
                row = visitor(i, row)
                if row:
                    writer.writerow(row)
    shutil.move(tmp, fname)


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

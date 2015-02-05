from __future__ import unicode_literals, print_function

from tsammalexdata.util import visit, data_file, jsonload


class Visitor(object):
    def __init__(self):
        self._data = {i['id']: i for i in jsonload(data_file('taxa.json'))}

    def __call__(self, index, row):
        row = row[:6] + ['phylum' if index == 0 else '', 'class' if index == 0 else ''] + row[6:]
        d = self._data.get(row[0])
        if d:
            for i, attr in enumerate('kingdom phylum class order family genus'.split()):
                if d.get(attr):
                    row[i + 5] = d[attr]
        return row


if __name__ == '__main__':
    visit('taxa.csv', Visitor())
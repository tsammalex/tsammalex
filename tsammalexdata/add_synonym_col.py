from __future__ import unicode_literals, print_function

from tsammalexdata.util import visit


class Visitor(object):
    def __call__(self, index, row):
        return row[:2] + ['synonyms' if index == 0 else ''] + row[2:]


if __name__ == '__main__':
    visit('taxa.csv', Visitor())
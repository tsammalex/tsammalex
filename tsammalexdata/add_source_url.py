from __future__ import unicode_literals, print_function
import json

from purl import URL

from tsammalexdata.util import visit, data_file


class Visitor(object):
    def __init__(self):
        self.cols = {}
        with open(data_file('images_md.json'), 'rb') as fp:
            self.md = json.load(fp)
        self.count = 0

    def __call__(self, index, row):
        if index == 0:
            self.cols = {col: i for i, col in enumerate(row)}
            return row

        url = URL(row[self.cols['src']])
        try:
            for filename in url.path_segments():
                if filename in self.md:
                    if self.md[filename].get('source_url'):
                        row[self.cols['source']] = self.md[filename]['source_url']
                        self.count += 1
                        break
        except IndexError:
            pass
        return row


if __name__ == '__main__':
    v = Visitor()
    visit('images.csv', v)
    print(v.count)
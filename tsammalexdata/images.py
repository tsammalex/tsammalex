import os
import shutil

from tsammalexdata.util import data_file, jsonload, jsondump, csv_items, visit
from tsammalexdata.image_providers import PROVIDERS, get_image_info, get_image


def update(p):
    data = jsonload(data_file('cn', 'images.json'), default={})
    try:
        info = None
        for img in csv_items('cn/' + p):
            key = '%s-%s' % (img['taxa__id'], img['tags'])
            if key in data:
                print('+++', img['id'] or img['source'], data[key]['source'])
                continue
            info = get_image_info(img)
            if info:
                data[key] = get_image(info, data_file('cn', 'images'))
    except:
        print('----->')
        print(img)
        if info:
            print(info)
        jsondump(data, data_file('cn', 'images.json'), indent=4)
        raise
    jsondump(data, data_file('cn', 'images.json'), indent=4)


class JSON2CSV(object):
    def __init__(self, data):
        self.data = jsonload(data)
        print(len(self.data))

    def __call__(self, index, row):
        #
        # TODO: merge code from update (and stage?) in here!!
        #
        if index == 0:
            self.cols = {col: i for i, col in enumerate(row)}
            return row
        key = '%s-%s' % (row[self.cols['taxa__id']], row[self.cols['tags']])
        row = [c.strip() for c in row]
        if key in self.data and self.data[key]['id']:
            info = self.data[key]
            for col in 'creator place permission comments'.split():
                if not row[self.cols[col]].strip() and info.get(col):
                    row[self.cols[col]] = info.get(col).strip().encode('utf8')

            for col in 'id date source source_url mime_type'.split():
                if info.get(col):
                    row[self.cols[col]] = info.get(col).encode('utf8')

            if 'latitude' in info and 'longitude' in info:
                row[self.cols['gps']] = '%s %s' % (info['latitude'], info['longitude'])
        return row


def rewrite(p):
    visit('cn/' + p, JSON2CSV(data_file('cn', 'images.json')))


def check(p):
    count = 0
    existing = [i['id'] for i in csv_items('cn/' + p) if 'edmond' in i['source_url']]
    for id, fname in [(n.split('.')[0], n) for n in os.listdir(data_file('cn/images'))]:
        if id in existing:
            count += 1
            os.remove(data_file('cn', 'images', fname))
    print(count)


class Selector(object):
    def __call__(self, index, row):
        if index == 0:
            self.cols = {col: i for i, col in enumerate(row)}
            return row
        if 'edmond.' in row[self.cols['source_url']]:
            return row


def select(p):
    shutil.copy(data_file('cn', p), data_file('cn', 'staged_images.csv'))
    visit('cn/staged_images.csv', Selector())
    print(len(open(data_file('cn', 'staged_images.csv')).read().split('\n')) - 1)


#-----------------------------------

class Deduplicator(object):
    def __init__(self, data):
        self.data = data
        self.count = 0

    def __call__(self, index, row):
        if index == 0 or row[0] not in self.data:
            return row
        self.count += 1


def dedup():
    existing = [i['id'] for i in csv_items('images.csv') if 'edmond' in i['source_url']]
    d = Deduplicator(existing)
    visit('cn/images.csv', d)
    print(d.count)


class RemoveUploaded(object):
    def __init__(self, data):
        self.data = data

    def __call__(self, index, row):
        if len(row) < 3:
            return row
        if index > 0 and (row[1], row[2]) not in self.data:
            return row


def do_check(fname):
    existing = {(i['taxa__id'], i['tags']): i for i in
                csv_items('images.csv') if 'edmond' in i['source_url']}
    visit(fname, RemoveUploaded(existing))
    #c = 0
    #for i, row in enumerate(csv_items(fname)):
    #    if (row['taxa__id'], row['tags']) in existing:
    #        if 0: #row['id'] != existing[(row['taxa__id'], row['tags'])]['source']:
    #            print(row)
    #            print(existing[(row['taxa__id'], row['tags'])])
    #        else:
    #            c += 1
    #print('%s of %s' % (c, i))


"""
(clld)robert@astroman:~/venvs/clld/data/tsammalex-data/tsammalexdata$ python images.py check cn/images_newLS150310.csv
1063 of 1169
(clld)robert@astroman:~/venvs/clld/data/tsammalex-data/tsammalexdata$ python images.py check cn/images_new_150304_NJ.csv
881 of 1039
(clld)robert@astroman:~/venvs/clld/data/tsammalex-data/tsammalexdata$ python images.py check cn/images_newCN150309final.csv
1219 of 1385

- download images and metadata
    python images.py update cn/images.csv

- rewrite cn/images.csv with metadata from cn/images.json:
    python images.py rewrite cn/images.csv

- upload images from cn/images to edmond
- run
    python edmond.py cn/images.csv

  to add edmond source urls
- move images to uploaded
- create staging file
    python images.py stage

- append rows from staging file to official images.csv (by hand)
- run nosetests
- remove rows from cn/images.csv
    python images.py purge
"""


if __name__ == '__main__':
    import sys
    #edmond_urls = file_urls(data_file('Edmond.xml'))

    #visit(sys.argv[1], CN())
    #sys.exit(0)

    cmd = sys.argv[1]
    if cmd == 'update':
        update(sys.argv[2])
    elif cmd == 'rewrite':
        rewrite(sys.argv[2])
    elif cmd == 'stage':
        check(sys.argv[2])
        select(sys.argv[2])
    elif cmd == 'purge':
        dedup()

    elif cmd == 'check':
        do_check(sys.argv[2])

    elif cmd == 'test':
        for provider in PROVIDERS:
            if hasattr(provider, '__example__'):
                url, info = provider.__example__
                res = provider.info(url)
                if res != info:
                    print('ERROR:')
                    for d in [res, info]:
                        for k in sorted(d.keys()):
                            print(k, d[k])
                else:
                    print('OK')
    else:
        raise ValueError(cmd)

from __future__ import unicode_literals, print_function
import sys
from xml.etree import ElementTree
from io import open
import re

import requests

from tsammalexdata.util import data_file, visit


URL = \
    "http://edmond.mpdl.mpg.de/imeji/export"\
    "?format=xml&type=image&n=10000&col=d2JGQRxO19XTOEXG&q="

#
# TODO: replace urls in images.csv, later: upload images to edmond, then replace urls.
#
qname = lambda localname: '{http://imeji.org/terms}' + localname


def get(e, k):
    return e.find(qname(k)).text


def file_urls(source):
    """Parse URL information from imeji XML.

    :param source: Path to a imeji collection metadata file in imeji XML format.
    :return: dict of (filename, infodict) pairs.
    """
    res = {}
    items = ElementTree.parse(source)
    for item in items.findall(qname('item')):
        data = dict(id=item.attrib['id'])
        for key in 'full web thumbnail'.split():
            data[key] = get(item, key + 'ImageUrl')
        # add an alias for the URL to the original file:
        data['url'] = data['full']
        res[get(item, 'filename')] = data
        res[get(item, 'checksum')] = data
    return res


class Visitor(object):
    """Visitor to update the source_url column in an images.csv file.

    Corresponding items in the Tsammalex collection on Edmond are detected by matching
    the id of the image against filename or checksum attribute of the Edmond item.
    """
    def __init__(self):
        self.edmond_urls = file_urls(data_file('Edmond.xml'))
        self.edmond_repls = [
            ('damaliscusdorcasphillpsi', 'damaliscuspygargusphillipsi'),
            ('felislybica', 'felissylvestrislybica'),
            ('felisserval', 'leptailurusserval'),
        ]
        self.type_pattern = re.compile('\-(large|small)\.')
        self.cols = {}

    def __call__(self, index, row):
        if index == 0:
            self.cols = {col: i for i, col in enumerate(row)}
            return row

        id_ = self.type_pattern.sub('.', row[self.cols['id']])
        if '-thumbnail' in id_:
            # remove thumbnail images
            return

        edmond_id = id_[:]
        for s, p in self.edmond_repls:
            edmond_id = edmond_id.replace(p, s)
        if edmond_id in self.edmond_urls:
            row[self.cols['source_url']] = self.edmond_urls[edmond_id]['full']
        else:
            #
            # FIXME: check whether source_url is an Edmond image URL, if not, upload the
            # image to Edmond, insert the URL here! Depends on the imeji API being
            # available on Edmond.
            #
            print(row[self.cols['id']])
        return row


if __name__ == '__main__':
    with open(data_file('Edmond.xml'), 'w', encoding='utf8') as fp:
        fp.write(requests.get(URL).text)
    visit(sys.argv[1] if len(sys.argv) > 1 else 'images.csv', Visitor())

from __future__ import unicode_literals, print_function
import sys
from xml.etree import ElementTree
from io import open

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
    :return: dict of (md5sum, infodict) pairs.
    """
    res = {}
    items = ElementTree.parse(source)
    for item in items.findall(qname('item')):
        data = dict(id=item.attrib['id'])
        for _key in 'full web thumbnail'.split():
            data[_key] = get(item, _key + 'ImageUrl')
        # add an alias for the URL to the original file:
        data['url'] = data['full']
        data['md5'] = get(item, 'checksum')
        res[get(item, 'checksum')] = data
    return res


class Visitor(object):
    """Visitor to update the source_url column in an images.csv file.

    Corresponding items in the Tsammalex collection on Edmond are detected by matching
    the id of the image against filename or checksum attribute of the Edmond item.
    """
    def __init__(self):
        self.edmond_urls = file_urls(data_file('Edmond.xml'))
        self.cols = {}
        self.count = 0

    def __call__(self, index, row):
        if index == 0:
            self.cols = {col: i for i, col in enumerate(row)}
            return row

        _id = row[self.cols['id']]

        if _id in self.edmond_urls:
            row[self.cols['source_url']] = self.edmond_urls[_id]['full']
            self.count += 1
        #else:
            #
            # FIXME: check whether source_url is an Edmond image URL, if not, upload the
            # image to Edmond, insert the URL here! Depends on the imeji API being
            # available on Edmond.
            #
        #    print(_id, row)
        return row


if __name__ == '__main__':
    with open(data_file('Edmond.xml'), 'w', encoding='utf8') as fp:
        fp.write(requests.get(URL).text)
    v = Visitor()
    visit(sys.argv[1] if len(sys.argv) > 1 else 'images.csv', v)
    print(v.count)

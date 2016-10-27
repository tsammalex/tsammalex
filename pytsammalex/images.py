from __future__ import unicode_literals, division, print_function
from mimetypes import guess_extension

from bs4 import BeautifulSoup
import requests
from requests.packages.urllib3.exceptions import (
    InsecurePlatformWarning, SNIMissingWarning,
)
from purl import URL
from clldutils.path import Path, TemporaryDirectory, copy, md5

from pytsammalex.models import Images

requests.packages.urllib3.disable_warnings(InsecurePlatformWarning)
requests.packages.urllib3.disable_warnings(SNIMissingWarning)


def download(url, out):
    r = requests.get(url)
    mimetype = r.headers['content-type']
    ext = guess_extension(mimetype, strict=False)
    if mimetype.startswith('image') and ext:
        fname = out.joinpath('image' + (ext if ext != '.jpe' else '.jpg'))
        with open(fname.as_posix(), 'wb') as fp:
            fp.write(r.content)
        return fname


class ImageProvider(object):
    """Given a URL of an accepted format, DataProviders can fetch metadata for an image.
    """
    def __init__(self, repos):
        self.repos = repos

    def __contains__(self, item):
        """
        Check whether the given url is recognized as belonging to this provider.

        :param url:
        :return:
        """
        return self.identify(item) is not None

    def identify(self, item):
        return

    def metadata(self, item):
        return {}

    @staticmethod
    def bs(markup):
        return BeautifulSoup(markup, 'html.parser')

    @staticmethod
    def get(url):
        return requests.get(url)

    @classmethod
    def url_parts(self, item):
        url = URL(item['id'])
        return url, url.host(), url.path_segments()

    def retrieve(self, item, cdstar_catalog, checksums, mediacatalog):
        """
        - download
        - compute checksum
        - upload to CDSTAR
        - add to cdstar.json

        :return: Image instance
        """
        md = self.metadata(item) or {}
        source_url = md.get('source_url')
        if not source_url:
            return
        with TemporaryDirectory() as tmp:
            if isinstance(source_url, Path):
                fname = tmp.joinpath(source_url.name)
                copy(source_url, fname)
            else:
                # download the thing
                fname = download(source_url, tmp)
                if not fname:
                    return
            # now upload to CDSTAR
            checksum = md5(fname)
            if checksum in checksums:
                raise ValueError('duplicate item {0} {1}'.format(item['id'], checksum))
            item.update(md)
            item['id'] = checksum
            item['collection'] = 'Tsammalex'
            img = Images.fromdict(item)
            if checksum not in mediacatalog.items:
                _, _, obj = list(cdstar_catalog.create(fname, item))[0]
                mediacatalog.add(obj)
            return img

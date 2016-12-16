# coding: utf8
from __future__ import unicode_literals, print_function, division
from mimetypes import guess_extension

from purl import URL
from clldutils.path import Path, TemporaryDirectory, copy, md5

from pytsammalex.models import Images
from pytsammalex.util import ExternalProviderMixin


class ImageProvider(ExternalProviderMixin):
    """Given a URL of an accepted format, ImageProviders can fetch an image and metadata.
    """
    def __init__(self, repos):
        self.repos = repos

    def __contains__(self, item):
        """
        Check whether the given url is recognized as belonging to this provider.

        :param item: A `models.Staged_images` instance.
        :return: Boolean indicating whether the ImageProvider recognizes the item or not.
        """
        return self.identify(item) is not None

    @classmethod
    def url_parts(self, url):
        url = URL(url)
        return url, url.host(), url.path_segments()

    def _download(self, url, out):
        r = self.get(url)
        mimetype = r.headers['content-type']
        ext = guess_extension(mimetype, strict=False)
        if mimetype.startswith('image') and ext:
            fname = out.joinpath('image' + (ext if ext != '.jpe' else '.jpg'))
            with open(fname.as_posix(), 'wb') as fp:
                fp.write(r.content)
            return fname

    def retrieve(self, item, cdstar_catalog, checksums, mediacatalog):
        """
        - download
        - compute checksum
        - upload to CDSTAR
        - add to cdstar.json

        :return: Image instance
        """
        md = self.metadata(item) or {}
        source_url = md.pop('source_url', None)
        if not source_url:
            return
        # We turn the Staged_images instance into a `dict`, which we will enrich and then
        # turn into an Images instance.
        item = dict(zip(item.fields(), item.csv_row()))
        with TemporaryDirectory() as tmp:
            if isinstance(source_url, Path):
                fname = tmp.joinpath(source_url.name)
                copy(source_url, fname)
            else:
                # download the thing
                fname = self._download(source_url, tmp)
                if not fname:
                    return
            checksum = md5(fname)
            if checksum in checksums:
                raise ValueError('duplicate item {0} {1}'.format(item['id'], checksum))
            item.update(md)
            item['id'] = checksum
            item['collection'] = 'Tsammalex'
            img = Images.fromdict(item)
            if checksum not in mediacatalog.items:
                # now upload to CDSTAR
                _, _, obj = list(cdstar_catalog.create(fname, item))[0]
                mediacatalog.add(obj)
            return img

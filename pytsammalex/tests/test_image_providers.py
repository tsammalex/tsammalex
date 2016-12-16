# coding: utf8
from __future__ import unicode_literals, print_function, division

from clldutils.testing import WithTempDir
from clldutils.path import md5
from mock import patch, MagicMock, Mock

from pytsammalex.tests.util import create_repos, MockRequests, MOCK_CDSTAR_OBJECT, fixtures
from pytsammalex.util import MediaCatalog
from pytsammalex.models import Staged_images


class Tests(WithTempDir):
    def test_ImageProvider(self):
        from pytsammalex.image_providers.base import ImageProvider

        repos = create_repos(self.tmp_path())
        prov = ImageProvider(repos)
        with self.assertRaises(NotImplementedError):
            'x' in prov
        self.assertEqual(len(prov.url_parts({'id': '/path'})), 3)

    def test_ImageProvider_retrieve(self):
        from pytsammalex.image_providers.base import ImageProvider

        repos = create_repos(self.tmp_path())
        fname = self.tmp_path('test')
        media = self.tmp_path(('media.json'))
        with fname.open('w', encoding='utf8') as fp:
            fp.write('test')

        class P(ImageProvider):
            def __init__(self, md):
                self._md = md
                ImageProvider.__init__(self, repos)

            def metadata(self, item):
                return self._md

        self.assertIsNone(P({}).retrieve(None, None, None, None))

        staged_image = Staged_images.fromdict({'id': 'abc', 'taxa__id': 'abc'})
        prov = P({'source_url': fname})
        with self.assertRaises(ValueError):
            prov.retrieve(staged_image, None, [md5(fname)], None)

        cdstar = MagicMock(
            create=MagicMock(return_value=[(None, None, MOCK_CDSTAR_OBJECT)]))
        prov = P({'source_url': 'x'})
        with patch('pytsammalex.util.requests', MockRequests()):
            with MediaCatalog(media.name, repos=repos) as mcat:
                prov.retrieve(staged_image, cdstar, [], mcat)
        self.assertTrue(cdstar.create.called)
        self.assertEqual(len(MediaCatalog(media.name, repos=repos)), 1)

    def test_ImageProviders_identify(self):
        from pytsammalex.image_providers.eol import Eol
        from pytsammalex.image_providers.flickr import Flickr
        from pytsammalex.image_providers.senckenberg import Senckenberg
        from pytsammalex.image_providers.wikimedia import Wikimedia
        from pytsammalex.image_providers.zimbabweflora import Zimbabweflora

        for prov in [Eol, Flickr, Senckenberg, Wikimedia, Zimbabweflora]:
            img = Staged_images.fromdict({'id': prov.__example__[0], 'taxa__id': 'abc'})
            self.assertIn(img, prov(None))

    def _provider_img_data(self, cls):
        prov = cls(None)
        return (
            prov,
            Staged_images.fromdict({'id': prov.__example__[0], 'taxa__id': 'abc'}),
            fixtures('image_providers', prov.__class__.__name__.lower()))

    def test_Senckenberg(self):
        from pytsammalex.image_providers.senckenberg import Senckenberg

        prov, img, data = self._provider_img_data(Senckenberg)
        with patch('pytsammalex.util.requests', MockRequests(text=data['metadata'])):
            self.assertEqual(
                prov.metadata(img)['source_url'],
                'http://www.westafricanplants.senckenberg.de/images/pictures/ficus_polita_img_04024_ralfbiechele_722_fc6e25.jpg')

    def test_Wikimedia(self):
        from pytsammalex.image_providers.wikimedia import Wikimedia

        prov, img, data = self._provider_img_data(Wikimedia)
        with patch('pytsammalex.util.requests', MockRequests(content=data['metadata'])):
            self.assertEqual(
                prov.metadata(img)['source_url'],
                'https://upload.wikimedia.org/wikipedia/commons/1/1d/Alcelaphus_caama.jpg')

    def test_Zimbabweflora(self):
        from pytsammalex.image_providers.zimbabweflora import Zimbabweflora

        prov, img, data = self._provider_img_data(Zimbabweflora)
        with patch('pytsammalex.util.requests', MockRequests(text=data['metadata'])):
            self.assertEqual(
                prov.metadata(img)['source_url'],
                'http://www.zimbabweflora.co.zw/speciesdata/images/10/100760-2.jpg')

    def test_Eol(self):
        from pytsammalex.image_providers.eol import Eol

        prov, img, data = self._provider_img_data(Eol)
        with patch('pytsammalex.util.requests', MockRequests(json=data['metadata'])):
            self.assertEqual(
                prov.metadata(img)['source_url'],
                'http://media.eol.org/content/2012/08/24/08/75619_orig.jpg')

    def test_Flickr(self):
        from pytsammalex.image_providers.flickr import Flickr

        prov, img, data = self._provider_img_data(Flickr)

        class Licenses(object):
            def getInfo(self):  # pragma: no cover
                return data['licenses']

        class Photos(object):
            licenses = Licenses()

            def getSizes(self, **kw):  # pragma: no cover
                return data['sizes']

            def getInfo(self, **kw):  # pragma: no cover
                return data['photo']

        class API(object):
            def __init__(self, *args, **kw):
                self.photos = Photos()

        with patch('pytsammalex.image_providers.flickr.FlickrAPI', API):
            # must re-initialize provider, because the patch for flickrapi may not have
            # been picked up!
            prov = Flickr(None)
            self.assertEqual(
                prov.metadata(img)['source_url'],
                'https://farm1.staticflickr.com/39/78968973_f30ad8c62d_o.jpg')

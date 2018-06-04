# coding: utf8
from __future__ import unicode_literals, print_function, division

import pytest
from clldutils.path import Path
from clldutils.path import md5
from mock import patch, MagicMock

from pytsammalex.image_providers import Eol, Flickr, Senckenberg, Wikimedia, \
    Zimbabweflora
from pytsammalex.image_providers.base import ImageProvider
from pytsammalex.models import Staged_images
from pytsammalex.tests.util import create_repos, MockRequests, \
    MOCK_CDSTAR_OBJECT, fixtures
from pytsammalex.util import MediaCatalog


def test_image_provider(tmpdir):
    repos = create_repos(tmpdir)
    prov = ImageProvider(repos)

    with pytest.raises(NotImplementedError):
        'x' in prov

    assert (len(prov.url_parts({'id': '/path'})) == 3)


def test_image_provider_retrieve(tmpdir):
    repos = create_repos(tmpdir)
    fname = tmpdir.join('test')

    with fname.open('w', encoding='utf8') as fp:
        fp.write('test')

    class TestProvider(ImageProvider):
        def identify(self, name):
            pass

        def __init__(self, md):
            self._md = md
            ImageProvider.__init__(self, repos)

        def metadata(self, item):
            return self._md

    assert (TestProvider({}).retrieve(None, None, None, None) is None)

    staged_image = Staged_images.fromdict({'id': 'abc', 'taxa__id': 'abc'})
    prov = TestProvider({'source_url': fname})

    with pytest.raises(ValueError):
        prov.retrieve(staged_image, None, [md5(fname)], None)

    cdstar = MagicMock(
        create=MagicMock(return_value=[(None, None, MOCK_CDSTAR_OBJECT)]))
    prov = TestProvider({'source_url': 'x'})

    with patch('pytsammalex.util.requests', MockRequests()):
        with MediaCatalog('media.json', repos=Path(repos)) as mcat:
            prov.retrieve(staged_image, cdstar, [], mcat)

    assert (cdstar.create.called is True)
    assert (len(MediaCatalog('media.json', repos=Path(repos))) == 1)


def test_image_providers_identify():
    for prov in [Eol, Flickr, Senckenberg, Wikimedia, Zimbabweflora]:
        img = Staged_images.fromdict(
            {'id': prov.__example__[0], 'taxa__id': 'abc'})

        assert img in prov(None)


def _provider_img_data(cls):
    prov = cls(None)
    return (
        prov,
        Staged_images.fromdict({'id': prov.__example__[0], 'taxa__id': 'abc'}),
        fixtures('image_providers', prov.__class__.__name__.lower()))


def test_senckenberg():
    prov, img, data = _provider_img_data(Senckenberg)
    with patch('pytsammalex.util.requests',
               MockRequests(text=data['metadata'])):
        assert (prov.metadata(img)['source_url'] ==
                'http://www.westafricanplants.senckenberg.de/images/pictures/'
                'ficus_polita_img_04024_ralfbiechele_722_fc6e25.jpg')


def test_wikimedia():
    prov, img, data = _provider_img_data(Wikimedia)
    with patch('pytsammalex.util.requests',
               MockRequests(content=data['metadata'])):
        assert (prov.metadata(img)['source_url'] ==
                'https://upload.wikimedia.org/wikipedia/'
                'commons/1/1d/Alcelaphus_caama.jpg')


def test_zimbabweflora():
    prov, img, data = _provider_img_data(Zimbabweflora)
    with patch('pytsammalex.util.requests',
               MockRequests(text=data['metadata'])):
        assert (prov.metadata(img)['source_url'] ==
                'http://www.zimbabweflora.co.zw/speciesdata/images/'
                '10/100760-2.jpg')


def test_eol():
    prov, img, data = _provider_img_data(Eol)
    with patch('pytsammalex.util.requests',
               MockRequests(json=data['metadata'])):
        assert (prov.metadata(img)['source_url'] ==
                'http://media.eol.org/content/2012/08/24/08/75619_orig.jpg')


def test_flickr():
    prov, img, data = _provider_img_data(Flickr)

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
        assert (prov.metadata(img)['source_url'] ==
                'https://farm1.staticflickr.com/39/78968973_f30ad8c62d_o.jpg')

# coding: utf8
from __future__ import unicode_literals, print_function, division

from pytsammalex.image_providers.eol import Eol
from pytsammalex.image_providers.flickr import Flickr
from pytsammalex.image_providers.senckenberg import Senckenberg
from pytsammalex.image_providers.wikimedia import Wikimedia
from pytsammalex.image_providers.zimbabweflora import Zimbabweflora
from pytsammalex.image_providers.fs import LocalFiles


PROVIDERS = [LocalFiles, Eol, Flickr, Senckenberg, Wikimedia, Zimbabweflora]

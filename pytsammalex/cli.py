from __future__ import unicode_literals, division, print_function
import os
import sys

from clldutils.clilib import ArgumentParser, ParserError
from clldutils.path import Path

import pytsammalex
from pytsammalex.commands import update_taxa, get_occurrences, upload_images, update_distribution

HOME = Path(os.path.expanduser('~'))


class ValidationError(ValueError):
    def __init__(self, msg):
        self.msg = msg
        ValueError.__init__(self, msg)


def main():
    parser = ArgumentParser('pytsammalex', update_taxa, get_occurrences, upload_images, update_distribution)
    parser.add_argument(
        '--tsammalex-data',
        help="path to tsammalex-data repository",
        default=Path(pytsammalex.__file__).parent.parent)
    sys.exit(parser.main())

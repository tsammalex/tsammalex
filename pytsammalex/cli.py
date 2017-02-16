from __future__ import unicode_literals, division, print_function
import os
import sys

from clldutils.clilib import ArgumentParserWithLogging
from clldutils.path import Path

import pytsammalex
import pytsammalex.commands

HOME = Path(os.path.expanduser('~'))


class ValidationError(ValueError):
    def __init__(self, msg):
        self.msg = msg
        ValueError.__init__(self, msg)


def main():
    parser = ArgumentParserWithLogging('pytsammalex')
    parser.add_argument(
        '--tsammalex-data',
        help="path to tsammalex-data repository",
        default=Path(pytsammalex.__file__).parent.parent)
    sys.exit(parser.main())

import sys

from tambo import Transport
import masapan
from masapan.runner import Run
from masapan.decorators import catches


class Masapan(object):
    _help = """
masapan: A coverage for statically defined rules, so that third party APIs can
be thoroughly tested.

Version: %s

Subcommands:
run                 Starts a new run, measuring coverage against passed in rules.

    """

    mapper = {'run': Run}

    def __init__(self, argv=None, parse=True):
        if argv is None:
            argv = sys.argv
        if parse:
            self.main(argv)

    def help(self):
        return self._help % (masapan.__version__)

    @catches(KeyboardInterrupt)
    def main(self, argv):
        parser = Transport(argv, mapper=self.mapper,
                           check_help=False,
                           check_version=False)
        parser.parse_args()
        parser.catch_help = self.help()
        parser.catch_version = masapan.__version__
        parser.mapper = self.mapper
        if len(argv) <= 1:
            return parser.print_help()
        parser.dispatch()
        parser.catches_help()
        parser.catches_version()

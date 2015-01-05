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

Global options:

--config            Define the config module (path to Python file)

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
        options = [['--config', '--conf']]
        parser = Transport(argv, mapper=self.mapper,
                           options=options,
                           check_help=False,
                           check_version=False)
        parser.parse_args()
        if parser.get('--config'):
            self.load_config_module(parser['--config'])
        parser.catch_help = self.help()
        parser.catch_version = masapan.__version__
        parser.mapper = self.mapper
        if len(argv) <= 1:
            return parser.print_help()
        parser.dispatch()
        parser.catches_help()
        parser.catches_version()

    def load_config_module(self, path):
        # be aware of same file path for relative imports
        import os
        old_path0   = sys.path[0]
        module_name = os.path.dirname(os.path.abspath(path))
        if module_name not in sys.path:
            sys.path[0] = module_name

        _file = open(path)
        compiled = compile(_file.read(), path, "exec")
        globals_ = {}
        exec(compiled, globals_)

        # restore the original sys.path
        sys.path[0] = old_path0

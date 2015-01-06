import sys
from core import Runner, FileCollector
import os


class Run(object):

    def __init__(self, argv=None):
        self.argv = argv

    def parse_args(self):
        valid_path = os.path.abspath(sys.argv[-1])
        collection = FileCollector(valid_path)

        r = Runner(collection, {})
        r.run()

        # report:
        from masapan.output import ReportResults
        ReportResults(r).report()


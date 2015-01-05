import sys
from core import Runner, FileCollector
import os


# reporting templates
report_header = """
Name                                                                Cases    Miss    Cover
------------------------------------------------------------------------------------------
"""

report_data = """
%s                                                                     %s      %s      %s%
"""

report_footer = """
------------------------------------------------------------------------------------------
TOTAL                                                                  %s      %s      %s%
"""
# XXX
report_errors = """
%s
"""

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


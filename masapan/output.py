import re
import sys
import traceback
from textwrap import dedent
from os.path     import dirname, abspath


class ReportResults(object):


    def __init__(self, results, writer=None):
        self.results = results
        self.config  = self.results.config
        self.writer  = writer
        if not self.writer:
            self.writer = Writer()


    def report(self):
        self.header()
        self.data()
        self.footer()
        self.writer.newline()
        if self.results.errors:
            self.errors()

    def header(self):
        report_header = dedent("""
        Name                                                                Cases    Miss    Cover
        ------------------------------------------------------------------------------------------
        """)
        self.writer.writeln(report_header, 'green')

    def data(self):
        lines = []
        report_data = "%-72s %-6s %-5s %s%%"

        for path in self.results.report.keys():
            self.writer.writeln(
                report_data % (
                    path,
                    len(self.results.report[path].keys()),
                    len(self.results.report[path].keys()),
                    100,
                ), 'green'
            )



    def errors(self):
        format_exc = ExcFormatter(self.results.errors, self.config, self.writer)
        format_exc.output_errors()


    def footer(self):
        self.results.total_cases = 1
        self.results.total_failures = 1
        out_footer(self.results.total_cases,
                self.results.total_failures,
                1,
                self.writer)




class TerminalWriter(object):


    def __init__(self, dotted):
        self.dotted = dotted
        self.writer = Writer()


    def green_spec(self, title):
        string = "    %s" % (name_convertion(title))
        if not self.dotted:
            self.writer.writeln(string, 'green')
        else:
            self.writer.println('.')
            self.writer.flush()


    def red_spec(self, title):
        string = "    %s" % (name_convertion(title))
        if not self.dotted:
            self.writer.writeln(string, 'red')
        else:
            self.writer.println('F')
            self.writer.flush()


    def out_case(self, title):
        if not self.dotted:
            self.writer.println("\n\n%s" % name_convertion(title))


    def out_bold(self, string):
        self.writer.write(string, 'bold')


    def skipping(self):
        if not self.dotted:
            self.write.println(' ...skipping')
        else:
            self.writer.println('S')
            self.writer.flush()



def out_footer(cases, missing, cover , std=None):
    if not std:
        std = Writer()

    report_footer = dedent("""
    ------------------------------------------------------------------------------------------
    TOTAL                                                                    %-6s %-7s %s%%\n
    """)
    footer = report_footer % (cases, missing, cover)
    std.writeln(footer, 'green')



def format_file_line(filename, line):
    return Writer().bold("%s:%s:\n" % (filename, line))



class ExcFormatter(object):


    def __init__(self, failures, config, std=None):
        self.config      = config
        self.failures    = failures
        self.failed_test = 1
        self.std = std
        if not self.std:
            self.std = Writer()


    def output_failures(self):
        self.std.writeln('Failures:\n---------', 'red')
        for failure in self.failures:
            self.single_exception(failure)


    def output_errors(self):
        self.std.writeln('\nErrors:\n-------', 'red')
        for error in self.failures:
            error = self.build_error_output(error)
            self.failure_header(error['description'])
            self.std.writeln("File: ", 'red')
            self.std.println(format_file_line(error['filename'], error['lineno']))
            #if self.config.get('traceback') and error['text']:
            self.std.writeln(error['text'], 'red')


    def build_error_output(self, error):
        exc = {}
        p_error = PrettyExc(error['failure'], error=True)
        exc['description'] = p_error.exception_description
        try: # See if we have info at the message level and use that
            exc['filename'] = p_error.exc_value.filename
            exc['lineno']   = p_error.exc_value.lineno
        except:
            exc['filename']    = p_error.exception_file
            exc['lineno']      = p_error.exception_line
        exc['text']        = p_error.formatted_exception
        return exc


    def single_exception(self, failure):
        exc        = failure.get('failure')
        name       = failure.get('exc_name')
        trace      = failure.get('trace')
        pretty_exc = PrettyExc(exc, debug=self.config.get('debug'))

        self.failure_header(pretty_exc.exception_description)
        starts = pretty_exc.exception_file_start
        ends = pretty_exc.exception_file_end

        if starts == ends:
            self.std.writeln("Starts and Ends: ", 'red')
            self.std.println(format_file_line(pretty_exc.exception_file_start, pretty_exc.exception_line_start))
        else:
            self.std.writeln("Starts: ", 'red')
            self.std.println(format_file_line(pretty_exc.exception_file_start, pretty_exc.exception_line_start))
            self.std.writeln("Ends: ", 'red')
            self.std.println(format_file_line(pretty_exc.exception_file_end, pretty_exc.exception_line_end))

        if self.config.get('traceback'):
            self.std.writeln(pretty_exc.formatted_exception)

    def failure_header(self, name):
        string = "\n%s ==> %s" % (self.failed_test, name)
        self.failed_test += 1
        self.std.writeln(string, 'red')


class PrettyExc(object):

    def __init__(self, exc_info, error=True, debug=True):
        self.error = error
        self.debug = debug
        self.exc_type, self.exc_value, self.exc_traceback = exc_info
        if self.error:
            self.exc_traceback =  self._last_traceback(self.exc_traceback)
        self.end_traceback        = self._last_traceback(self.exc_traceback)
        self.exception_file_start = self.exc_traceback.tb_frame.f_code.co_filename
        self.exception_line_start = self.exc_traceback.tb_lineno
        self.exception_file_end   = self.end_traceback.tb_frame.f_code.co_filename
        self.exception_line_end   = self.end_traceback.tb_lineno
        self.exception_line       = self.exc_traceback.tb_lineno
        self.exception_file       = self.exc_traceback.tb_frame.f_code.co_filename
        self.exc_info             = exc_info


    @property
    def formatted_exception(self):
        traceback_lines = traceback.format_exception(self.exc_type,
                                                     self.exc_value,
                                                     self.exc_traceback)
        rewritten = self.translate_exc_line(traceback_lines)
        return ''.join(rewritten)


    def translate_exc_line(self, lines):
        return lines
        if self.error or self.debug: return lines
        valid_file_name   = re.compile(r'\s+File\s+(.*)case[_a-z]\w*\.py', re.IGNORECASE)
        valid_method_name = re.compile(r'(.*)\s+in\s+it_[_a-z]\w*', re.IGNORECASE)
        valid_it_case     = re.compile(r'it_[_a-z]\w*', re.IGNORECASE)
        rewritten_lines   = []
        for line in lines:
            if valid_file_name.match(line) and valid_method_name.match(line):
                it_method = valid_it_case.search(line)
                if it_method:
                    rewrite_it = name_convertion(it_method.group(), capitalize=False)
                    line = re.sub(valid_it_case, rewrite_it, line)
                rewritten_lines.append(line)
            else:
                rewritten_lines.append(line)
        return rewritten_lines


    @property
    def indented_traceback(self):
        trace = self.formatted_exception.split('\n')
        add_indent = ["    "+i for i in trace]
        return '\n'.join(add_indent)


    @property
    def exception_description(self):
        desc = traceback.format_exception_only(self.exc_type, self.exc_value)
        return self._short_exception_description(desc)


    def _short_exception_description(self, exception_description_lines):
        return exception_description_lines[-1].strip()


    def _last_traceback(self, tb):
        if tb is None: return tb
        while tb.tb_next:
            tb = tb.tb_next
        return tb



class Writer(object):


    def __init__(self, stdout=None):
        if not stdout:
            self.stdout = sys.__stdout__
        else:
            self.stdout = stdout
        self.out    = self.stdout.write
        self.isatty = self.stdout.isatty()
        self.flush  = self.stdout.flush


    def color(self, form):
        if not self.isatty or self.is_windows: return ''
        if form == None: return ''
        available = dict(
                blue   = '\033[94m',
                green  = '\033[92m',
                yellow = '\033[93m',
                red    = '\033[91m',
                bold   = '\033[1m',
                ends   = '\033[0m'
            )
        try:
            return available[form]
        except:
            raise KeyError('%s is not a valid format/color' % form)


    @property
    def is_windows(self):
        if sys.platform == 'win32':
            return True
        return False


    def println(self, string):
        self.out("%s" % string)


    def write(self, string, form):
        """No new line before or after"""
        color   = self.color(form)
        ends    = self.color('ends')
        out_str = "%s%s%s" % (color, string, ends)
        self.out(out_str)


    def writeln(self, string, form=None):
        """With a new line before and after"""
        color   = self.color(form)
        ends    = self.color('ends')
        out_str = "\n%s%s%s" % (color, string, ends)
        self.out(out_str)


    def newline(self, lines=1):
        nln = '\n'*lines
        self.out(nln)


    def green(self, string):
        """
        Makes incoming string output as green on the terminal
        """
        color   = self.color('green')
        ends    = self.color('ends')
        color_it = "%s%s%s" % (color, string, ends)
        return color_it


    def red(self, string):
        """
        Makes incoming string output as red on the terminal
        """
        color   = self.color('red')
        ends    = self.color('ends')
        color_it = "%s%s%s" % (color, string, ends)
        return color_it


    def bold(self, string):
        """
        Makes text bold in the terminal
        """
        color   = self.color('bold')
        ends    = self.color('ends')
        bold_it = "%s%s%s" % (color, string, ends)
        return bold_it



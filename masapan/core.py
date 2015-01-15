import sys
import os
import re
import imp
from masapan import registration


def globals_from_file(filename):
    # be aware of same file path for relative imports
    old_path0 = sys.path[0]
    sys.path[0] = os.path.dirname(filename)

    _file = open(filename)
    compiled = compile(_file.read(), filename, "exec")

    # Next, attempt to actually import the file as a module.
    # This provides more verbose import-related error reporting than exec()
    absname, _ = os.path.splitext(filename)
    basepath, module_name = absname.rsplit(os.sep, 1)
    # At some point, when/if we get to need py3 compatibility
    #if python3:
        #SourceFileLoader(module_name, abspath).load_module(module_name)
    #else:
    imp.load_module(
        module_name,
        *imp.find_module(module_name, [basepath])
    )

    globals_ = {}
    globals_['__file__'] = filename
    exec(compiled, globals_)

    # restore the original sys.path
    sys.path[0] = old_path0
    return globals_


class FileCollector(list):

    def __init__(self, path, config={}):
        self.user_match       = config.get('collect-match')
        self.case_insensitive = config.get('collect-ci')
        self.path             = path
        self._collect()


    @property
    def valid_module_name(self):
        fallback = re.compile(r'test[_a-z]\w*\.py$', re.IGNORECASE)
        if not self.user_match:
            return fallback
        else:
            try:
                if self.case_insensitive:
                    return re.compile(self.user_match, re.IGNORECASE)
                return re.compile(self.user_match)
            except Exception, msg:
                raise SystemExit('Could not compile regex, error was: %s' % msg)


    def _collect(self):
        if os.path.isfile(self.path):
            self.append(self.path)
            return

        # Local is faster
        walk = os.walk
        join = os.path.join
        path = self.path
        levels_deep = 0

        for root, dirs, files in walk(path):
            levels_deep += 1

            # Start checking for Python packages after 3 levels
            if levels_deep > 2:
                if not '__init__.py' in files:
                    continue
            for item in files:
                absolute_path = join(root, item)
                if not self.valid_module_name.match(item):
                    continue
                self.append(absolute_path)

from collections import defaultdict


class Runner(object):

    def __init__(self, paths, config):
        self.config         = config
        self.paths          = paths
        self.errors         = []
        self.profiles       = []
        self.total_errors   = 0
        self.class_name     = config.get('class_name')
        self.method_name    = config.get('method_name')
        self.report = defaultdict(dict)


    def run(self):
        registry_paths = registration.registry.keys()
        for f in self.paths:
            path_is_valid = any([f.startswith(p) for p in registry_paths])
            if path_is_valid:
                try:
                    classes = get_classes(f, self.class_name)
                except Exception, e:
                    self.total_errors += 1
                    self.errors.append(
                        dict(
                            failure=sys.exc_info(),
                            exc_name=e.__class__.__name__
                            )
                        )
                    continue
                test_module = self.report[f]
                for case in classes:
                    test_module.setdefault(case.__name__, [])

                    methods = get_methods(case, self.method_name)
                    test_module[case.__name__] =  methods or []

#
# Runner helpers
#

def get_classes(filename, class_name):
    if class_name:
        classes = [i for i in _collect_classes(filename)
                    if class_name == get_class_name(i)]
    else:
        classes = [i for i in _collect_classes(filename)]

    return classes



def get_methods(suite, method_name):
    if method_name:
        methods = [i for i in _collect_methods(suite)
                    if i == method_name]
    else:
        methods = _collect_methods(suite)

    return methods



def _collect_classes(path):
    global_modules = map(globals_from_file, [path])
    return [i for i in global_modules[0].values() if callable(i) and getattr(i, '__name__', '').startswith('Test')]



def _collect_methods(module):
    valid_method_name = re.compile(r'test_[_a-z]\w*$', re.IGNORECASE)
    return [i for i in dir(module) if valid_method_name.match(i)]

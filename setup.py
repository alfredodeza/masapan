import os
import re

readme = os.path.join(os.path.dirname(__file__), 'README.rst')
LONG_DESCRIPTION = open(readme).read()

module_file = open("masapan/__init__.py").read()
metadata = dict(re.findall("__([a-z]+)__\s*=\s*'([^']+)'", module_file))


from setuptools import setup

setup(
    name             = 'masapan',
    description      = 'A static coverage framework',
    packages         = ['masapan'],
    author           = 'Alfredo Deza',
    author_email     = 'contact [at] deza.pe',
    version          = metadata['version'],
    license          = "MIT",
    zip_safe         = False,
    keywords         = "test, coverage, framework",
    scripts = ['bin/masapan'],
    long_description = LONG_DESCRIPTION,
    install_requires = ['tambo'],
    classifiers      = [
                        'Development Status :: 4 - Beta',
                        'Intended Audience :: Developers',
                        'License :: OSI Approved :: MIT License',
                        'Topic :: Software Development :: Libraries',
                        'Topic :: Utilities',
                        'Operating System :: MacOS :: MacOS X',
                        'Operating System :: Microsoft :: Windows',
                        'Operating System :: POSIX',
                        'Programming Language :: Python :: 2.5',
                        'Programming Language :: Python :: 2.6',
                        'Programming Language :: Python :: 2.7',
                        'Programming Language :: Python :: 3.3',
                        'Programming Language :: Python :: Implementation :: PyPy'
                      ],
)

#!/usr/bin/env python

import os.path
import re
import sys

from setuptools import setup, find_packages
from setuptools.command.test import test as TestCommand


class PyTest(TestCommand):
    user_options = [('pytest-args=', 'a', "Arguments to pass to py.test")]

    def initialize_options(self):
        TestCommand.initialize_options(self)
        self.pytest_args = []

    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        #import here, cause outside the eggs aren't loaded
        import pytest
        errno = pytest.main(self.pytest_args)
        sys.exit(errno)


curdir = os.path.dirname(os.path.realpath(__file__))
filename = os.path.join(curdir, 'ipymd', '__init__.py')
with open(filename, 'r') as f:
    version = re.search(r"__version__ = '([^']+)'", f.read()).group(1)

classes = """
    Development Status :: 3 - Alpha
    License :: OSI Approved :: BSD License
    Environment :: Console
    Framework :: IPython
    Intended Audience :: Developers
    Natural Language :: English
    Operating System :: Unix
    Operating System :: POSIX
    Operating System :: MacOS :: MacOS X
    Programming Language :: Python
    Programming Language :: Python :: 2
    Programming Language :: Python :: 2.7
    Programming Language :: Python :: 3
    Programming Language :: Python :: 3.3
    Programming Language :: Python :: 3.4
    Topic :: Software Development :: Libraries
    Topic :: Text Processing :: Markup

"""
classifiers = [s.strip() for s in classes.split('\n') if s]

description = ('Use the IPython notebook as an interactive Markdown editor')

with open('README.md') as f:
    long_description = f.read()

setup(
    name='ipymd',
    version=version,
    license='BSD',
    description=description,
    long_description=long_description,
    author='Cyrille Rossant',
    author_email='cyrille.rossant at gmail.com',
    maintainer='Cyrille Rossant',
    maintainer_email='cyrille.rossant at gmail.com',
    url='https://github.com/rossant/ipymd',
    classifiers=classifiers,
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'ipymd=ipymd.core.scripts:main',
        ],
        'ipymd.format': [
            'markdown=ipymd.formats.markdown:MARKDOWN_FORMAT',
            'atlas=ipymd.formats.atlas:ATLAS_FORMAT',
            'notebook=ipymd.formats.notebook:NOTEBOOK_FORMAT',
            'opendocument=ipymd.formats.opendocument:ODF_FORMAT[odf]',
            'python=ipymd.formats.python:PYTHON_FORMAT',
        ]
    },
    install_requires=['pyyaml'],
    extras_require={
        'odf': ['odfpy'],
    },
    cmdclass={'test': PyTest},
)

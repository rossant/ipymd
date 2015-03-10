# -*- coding: utf-8 -*-

"""Testing utilities."""

#------------------------------------------------------------------------------
# Imports
#------------------------------------------------------------------------------

import os
import os.path as op
import difflib
from pprint import pprint

from ...core.format_manager import format_manager, convert
from ...core.scripts import _load_file, _save_file
from ...ext.six import exec_


#------------------------------------------------------------------------------
# Test Markdown parser
#------------------------------------------------------------------------------

def _script_dir():
    return op.dirname(op.realpath(__file__))


def _test_file_path(basename, format=None):
    """Return the full path to an example filename in the 'examples'
    directory."""
    if format is not None:
        file_extension = format_manager().file_extension(format)
        filename = basename + '.' + format + file_extension
    else:
        # format=None ==> .py test file
        filename = basename + '.py'
    return op.realpath(op.join(_script_dir(), '../../../examples', filename))


def _exec_test_file(basename):
    """Return the 'output' object defined in a Python file."""
    path = _test_file_path(basename)
    with open(path, 'r') as f:
        contents = f.read()
    ns = {}
    exec_(contents, ns)
    return ns.get('output', None)


def _read_test_file(basename, format):
    """Read a test file."""
    path = _test_file_path(basename, format)
    return _load_file(path, format)


def _test_reader(basename, format):
    """Return converted and expected ipymd cells of a given example."""
    contents = _read_test_file(basename, format)
    converted = convert(contents, from_=format)
    expected = _exec_test_file(basename)
    return converted, expected


def _test_writer(basename, format):
    """Return converted and expected ipymd cells of a given example."""
    cells = _exec_test_file(basename)
    converted = convert(cells, to=format)
    expected = _read_test_file(basename, format)
    return converted, expected

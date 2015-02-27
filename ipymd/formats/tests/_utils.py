# -*- coding: utf-8 -*-

"""Testing utilities."""

#------------------------------------------------------------------------------
# Imports
#------------------------------------------------------------------------------

import os
import os.path as op
import difflib
from pprint import pprint

from ...core import format_manager, convert
from ...scripts import _read_file, _write_file
from ...six import exec_


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
    return _read_file(path, format)


#------------------------------------------------------------------------------
# Test Markdown parser
#------------------------------------------------------------------------------


def _diff_removed_lines(diff):
    return ''.join(x[2:] for x in diff if x.startswith('- '))


def _diff(text_0, text_1):
    """Return a diff between two strings."""
    diff = difflib.ndiff(text_0.splitlines(), text_1.splitlines())
    return _diff_removed_lines(diff)


def _show_outputs(*outputs):
    for output in outputs:
        print()
        print("-" * 30)
        pprint(output)


#------------------------------------------------------------------------------
# Test Markdown parser
#------------------------------------------------------------------------------

def _test_reader(basename, format):
    """Return converted and expected ipymd cells of a given example."""

    file_extension = format_manager().file_extension(format)

    # File name structure: ex1.markdown.md or ex2.notebook.ipynb
    contents = _read_test_file(basename, format)

    # Convert to ipymd cells.
    converted = convert(contents, from_=format)

    # Load the expected ipymd cells.
    expected = _exec_test_file(basename)

    return converted, expected


def _test_writer(basename, format):
    """Return converted and expected ipymd cells of a given example."""

    file_extension = format_manager().file_extension(format)

    # Load the source ipymd cells.
    cells = _exec_test_file(basename)

    # Convert to ipymd cells.
    converted = convert(cells, to=format)

    # File name structure: ex1.markdown.md or ex2.notebook.ipynb
    expected = _read_test_file(basename, format)

    return converted, expected

# -*- coding: utf-8 -*-

"""Utils"""

#------------------------------------------------------------------------------
# Imports
#------------------------------------------------------------------------------

import os
import os.path as op
import difflib

from .six import exec_, string_types


#------------------------------------------------------------------------------
# Utils
#------------------------------------------------------------------------------

def _script_dir():
    return op.dirname(op.realpath(__file__))


def _test_file_path(filename):
    """Return the full path to an example filename in the 'examples'
    directory."""
    return op.realpath(op.join(_script_dir(), '../examples', filename))


def _exec_test_file(filename):
    """Return the 'output' object defined in a Python file."""
    path = _test_file_path(filename)
    with open(path, 'r') as f:
        contents = f.read()
    ns = {}
    exec_(contents, ns)
    return ns.get('output', None)


def _read_test_file(filename):
    """Read a test file."""
    path = _test_file_path(filename)
    with open(path, 'r') as f:
        return f.read()


def _ensure_string(source):
    """Ensure a source is a string."""
    if isinstance(source, string_types):
        return source.rstrip()
    else:
        return '\n'.join([line.rstrip() for line in source]).rstrip()


def _diff_removed_lines(diff):
    return ''.join(x[2:] for x in diff if x.startswith('- '))


def _diff(text_0, text_1):
    """Return a diff between two strings."""
    diff = difflib.ndiff(text_0.splitlines(), text_1.splitlines())
    return _diff_removed_lines(diff)

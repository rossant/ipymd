# -*- coding: utf-8 -*-

"""Test Python parser and reader."""

#------------------------------------------------------------------------------
# Imports
#------------------------------------------------------------------------------

from ...core.core import format_manager, convert
from ...utils.utils import _remove_output
from ._utils import (_test_reader, _test_writer, _diff, _show_outputs,
                     _exec_test_file, _read_test_file)


#------------------------------------------------------------------------------
# Test Python parser
#------------------------------------------------------------------------------

def _test_python_reader(basename):
    """Check that (test cells) and (test contents ==> cells) are the same."""
    converted, expected = _test_reader(basename, 'python')
    assert _remove_output(converted) == _remove_output(expected)


def _test_python_writer(basename):
    """Check that (test contents) and (test cells ==> contents) are the same.
    """
    converted, expected = _test_writer(basename, 'python')
    assert _diff(converted, expected) == ''


def _test_python_python(basename):
    """Check that the double conversion is the identity."""

    contents = _read_test_file(basename, 'python')
    cells = convert(contents, from_='python')
    converted = convert(cells, to='python')

    assert _diff(contents, converted) == ''


def test_python_reader():
    _test_python_reader('ex1')
    _test_python_reader('ex2')


def test_python_writer():
    _test_python_writer('ex1')
    _test_python_writer('ex2')


def test_python_python():
    _test_python_python('ex1')
    _test_python_python('ex2')

# -*- coding: utf-8 -*-

"""Test notebook parser and reader."""

#------------------------------------------------------------------------------
# Imports
#------------------------------------------------------------------------------

from ...core.format_manager import format_manager, convert
from ..notebook import _compare_notebooks
from ...utils.utils import _diff, _show_outputs
from ._utils import (_test_reader, _test_writer,
                     _exec_test_file, _read_test_file)


#------------------------------------------------------------------------------
# Test notebook parser
#------------------------------------------------------------------------------

def _test_notebook_reader(basename):
    """Check that (test cells) and (test nb ==> cells) are the same."""
    converted, expected = _test_reader(basename, 'notebook')
    assert converted == expected


def _test_notebook_writer(basename):
    """Check that (test nb) and (test cells ==> nb) are the same.
    """
    converted, expected = _test_writer(basename, 'notebook')
    assert _compare_notebooks(converted, expected)


def _test_notebook_notebook(basename):
    """Check that the double conversion is the identity."""

    contents = _read_test_file(basename, 'notebook')
    cells = convert(contents, from_='notebook')
    converted = convert(cells, to='notebook')

    assert _compare_notebooks(contents, converted)


def test_notebook_reader():
    _test_notebook_reader('ex1')
    _test_notebook_reader('ex2')


def test_notebook_writer():
    _test_notebook_writer('ex1')
    _test_notebook_writer('ex2')


def test_notebook_notebook():
    _test_notebook_notebook('ex1')
    _test_notebook_notebook('ex2')

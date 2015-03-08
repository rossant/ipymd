# -*- coding: utf-8 -*-

"""Test ODF parser and reader."""

#------------------------------------------------------------------------------
# Imports
#------------------------------------------------------------------------------

from ...core.core import format_manager, convert
from ...utils.utils import _remove_output
from ._utils import (_test_reader, _test_writer, _diff, _show_outputs,
                     _exec_test_file, _read_test_file)


#------------------------------------------------------------------------------
# Test ODF parser
#------------------------------------------------------------------------------

def _test_odf_reader(basename):
    """Check that (test cells) and (test contents ==> cells) are the same."""
    converted, expected = _test_reader(basename, 'opendocument')
    assert _remove_output(converted) == _remove_output(expected)


def _test_odf_writer(basename):
    """Check that (test contents) and (test cells ==> contents) are the same.
    """
    converted, expected = _test_writer(basename, 'opendocument')
    assert _diff(converted, expected) == ''


def _test_odf_odf(basename):
    """Check that the double conversion is the identity."""

    contents = _read_test_file(basename, 'opendocument')
    cells = convert(contents, from_='opendocument')
    converted = convert(cells, to='opendocument')

    assert _diff(contents, converted) == ''


def test():
    markdown = _read_test_file('ex1', 'markdown')
    odf = convert(markdown, from_='markdown', to='opendocument')
    # TODO: check
    assert odf


# def test_odf_reader():
#     _test_odf_reader('ex1')
#     _test_odf_reader('ex2')


# def test_odf_writer():
#     _test_odf_writer('ex1')
#     _test_odf_writer('ex2')


# def test_odf_odf():
#     _test_odf_odf('ex1')
#     _test_odf_odf('ex2')

# -*- coding: utf-8 -*-

"""Test Markdown parser and reader."""

#------------------------------------------------------------------------------
# Imports
#------------------------------------------------------------------------------

from ._utils import _test_reader, _test_writer, _diff, _show_outputs


#------------------------------------------------------------------------------
# Test Markdown parser
#------------------------------------------------------------------------------

def _test_markdown_reader(basename):
    """Check that (test cells) and (test contents ==> cells) are the same."""
    converted, expected = _test_reader(basename, 'markdown')
    assert converted == expected


def _test_markdown_writer(basename):
    """Check that (test contents) and (test cells ==> contents) are the same.
    """
    converted, expected = _test_writer(basename, 'markdown')
    assert _diff(converted, expected) == ''


def test_markdown_reader():
    _test_markdown_reader('ex1')
    _test_markdown_reader('ex2')


def test_markdown_writer():
    _test_markdown_writer('ex1')
    _test_markdown_writer('ex2')

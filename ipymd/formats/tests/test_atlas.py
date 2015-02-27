# -*- coding: utf-8 -*-

"""Test Atlas parser and reader."""

#------------------------------------------------------------------------------
# Imports
#------------------------------------------------------------------------------

from ._utils import _test_reader, _test_writer, _diff


#------------------------------------------------------------------------------
# Test Atlas parser
#------------------------------------------------------------------------------

def _test_atlas_reader(basename):
    """Check that (test cells) and (test contents ==> cells) are the same."""
    converted, expected = _test_reader(basename, 'atlas')
    assert converted == expected


def _test_atlas_writer(basename):
    """Check that (test contents) and (test cells ==> contents) are the same.
    """
    converted, expected = _test_writer(basename, 'atlas')
    assert _diff(converted, expected) == ''


def test_atlas_reader():
    _test_atlas_reader('ex1')
    _test_atlas_reader('ex2')


def test_atlas_writer():
    _test_atlas_writer('ex1')
    _test_atlas_writer('ex2')

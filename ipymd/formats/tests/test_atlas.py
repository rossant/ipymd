# -*- coding: utf-8 -*-

"""Test Atlas parser and reader."""

#------------------------------------------------------------------------------
# Imports
#------------------------------------------------------------------------------

from ...core import format_manager, convert
from ._utils import (_test_reader, _test_writer, _diff, _show_outputs,
                     _exec_test_file, _read_test_file)


#------------------------------------------------------------------------------
# Test Atlas parser
#------------------------------------------------------------------------------

def _test_atlas_reader(basename):
    """Check that (test cells) and (test contents ==> cells) are the same."""
    converted, expected = _test_reader(basename, 'atlas')

    # Assert all cells are identical except the outputs which are lost
    # in translation.
    for cell_0, cell_1 in zip(converted, expected):
        assert cell_0['cell_type'] == cell_1['cell_type']
        ct = cell_0['cell_type']
        if ct == 'code':
            assert cell_0['input'] == cell_1['input']
        elif ct == 'markdown':
            assert cell_0['source'] == cell_1['source']
        else:
            raise RuntimeError()


def _test_atlas_writer(basename):
    """Check that (test contents) and (test cells ==> contents) are the same.
    """
    converted, expected = _test_writer(basename, 'atlas')
    assert _diff(converted, expected) == ''


def _test_atlas_atlas(basename):
    """Check that the double conversion is the identity."""

    contents = _read_test_file(basename, 'atlas')
    cells = convert(contents, from_='atlas')
    converted = convert(cells, to='atlas')

    assert _diff(contents, converted) == ''


def test_atlas_reader():
    _test_atlas_reader('ex1')
    _test_atlas_reader('ex2')


def test_atlas_writer():
    _test_atlas_writer('ex1')
    _test_atlas_writer('ex2')


def test_atlas_atlas():
    _test_atlas_atlas('ex1')
    _test_atlas_atlas('ex2')


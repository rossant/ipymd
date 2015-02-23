# -*- coding: utf-8 -*-

"""Test Atlas parser and reader.
"""

#------------------------------------------------------------------------------
# Imports
#------------------------------------------------------------------------------

from ..utils import _test_file_path, _exec_test_file, _diff, _show_outputs
from ..atlas import (AtlasReader, AtlasWriter,
                     atlas_to_ipymd_cells,
                     ipymd_cells_to_atlas)


#------------------------------------------------------------------------------
# Test Atlas parser
#------------------------------------------------------------------------------

def _test_atlas_reader(basename):
    """Assert that test ipymd cells and test md ==> cells are the same."""
    # Open a Atlas test file.
    with open(_test_file_path(basename + '.atlas.md'), 'r') as f:
        contents = f.read()

    # Convert to ipymd cells.
    cells = atlas_to_ipymd_cells(contents)

    # Load the expected ipymd cells.
    expected_cells = _exec_test_file(basename + '.atlas.py')

    # Compare.
    assert cells == expected_cells


def _test_atlas_writer(basename):
    """Check that md and ipymd cells ==> md are the same."""
    # Read the test ipymd cells.
    cells = _exec_test_file(basename + '.atlas.py')

    # Convert the ipymd cells to Atlas.
    contents = ipymd_cells_to_atlas(cells)

    # Open a Atlas test file.
    with open(_test_file_path(basename + '.atlas.md'), 'r') as f:
        expected_contents = f.read()

    assert _diff(contents, expected_contents) == ''


def test_atlas_reader():
    _test_atlas_reader('ex1')


def test_atlas_writer():
    _test_atlas_writer('ex1')

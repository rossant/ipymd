# -*- coding: utf-8 -*-

"""Test Markdown parser and reader.
"""

#------------------------------------------------------------------------------
# Imports
#------------------------------------------------------------------------------

from ..utils import _test_file_path, _exec_test_file, _diff, _show_outputs
from ..markdown import (MarkdownReader, MarkdownWriter,
                        markdown_to_ipymd_cells,
                        ipymd_cells_to_markdown)


#------------------------------------------------------------------------------
# Test Markdown parser
#------------------------------------------------------------------------------

def _test_markdown_reader(basename):
    """Assert that test ipymd cells and test md ==> cells are the same."""
    # Open a Markdown test file.
    with open(_test_file_path(basename + '.md'), 'r') as f:
        contents = f.read()

    # Convert to ipymd cells.
    cells = markdown_to_ipymd_cells(contents)

    # Load the expected ipymd cells.
    expected_cells = _exec_test_file(basename + '.py')

    # Compare.
    assert cells == expected_cells


def test_markdown_reader():
    _test_markdown_reader('ex1')


def _test_markdown_writer(basename):
    """Check that md and ipymd cells ==> md are the same."""
    # Read the test ipymd cells.
    cells = _exec_test_file(basename + '.py')

    # Convert the ipymd cells to Markdown.
    contents = ipymd_cells_to_markdown(cells)

    # Open a Markdown test file.
    with open(_test_file_path(basename + '.md'), 'r') as f:
        expected_contents = f.read()

    assert _diff(contents, expected_contents) == ''


def test_markdown_writer():
    _test_markdown_writer('ex1')

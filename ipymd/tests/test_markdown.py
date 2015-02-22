# -*- coding: utf-8 -*-

"""Test Markdown parser and reader.
"""

#------------------------------------------------------------------------------
# Imports
#------------------------------------------------------------------------------

from ..utils import _test_file_path, _exec_test_file, _diff
from ..markdown import MarkdownReader, MarkdownWriter, ipymd_cells_to_markdown


#------------------------------------------------------------------------------
# Test Markdown parser
#------------------------------------------------------------------------------

def test_base_markdown_reader():
    """Assert that test ipymd cells and test md ==> cells are the same."""
    # Open a Markdown test file.
    with open(_test_file_path('markdown_simple.md'), 'r') as f:
        contents = f.read()

    expected_cells = _exec_test_file('markdown_simple.py')

    # Read the Markdown file.
    reader = MarkdownReader()
    for cell, expected_cell in zip(reader.read(contents), expected_cells):
        assert cell == expected_cell


def test_base_markdown_writer():
    """Check that md and ipymd cells ==> md are the same."""
    # Read the test ipymd cells.
    cells = _exec_test_file('markdown_simple.py')

    # Convert the ipymd cells to Markdown.
    contents = ipymd_cells_to_markdown(cells)

    # Open a Markdown test file.
    with open(_test_file_path('markdown_simple.md'), 'r') as f:
        expected_contents = f.read()

    assert _diff(contents, expected_contents) == ''

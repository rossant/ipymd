# -*- coding: utf-8 -*-

"""Test Markdown parser and reader.
"""

#------------------------------------------------------------------------------
# Imports
#------------------------------------------------------------------------------

from ..utils import _test_file_path, _exec_test_file
from ..markdown import MarkdownReader


#------------------------------------------------------------------------------
# Test Markdown parser
#------------------------------------------------------------------------------

def test_base_markdown_reader():
    # Open a Markdown test file.
    with open(_test_file_path('markdown_simple.md'), 'r') as f:
        contents = f.read()

    expected_cells = _exec_test_file('markdown_simple.py')

    # Read the Markdown file.
    reader = MarkdownReader()
    for cell, expected_cell in zip(reader.read(contents), expected_cells):
        assert cell == expected_cell

# -*- coding: utf-8 -*-

"""Test Markdown parser and reader.
"""

#------------------------------------------------------------------------------
# Imports
#------------------------------------------------------------------------------

from ..utils import _test_file_path
from ..markdown import MarkdownReader


#------------------------------------------------------------------------------
# Test Markdown parser
#------------------------------------------------------------------------------

def test_base_markdown_reader():
    # Open a Markdown test file.
    with open(_test_file_path('markdown_simple.md'), 'r') as f:
        contents = f.read()

    expected_cells = [

        {'cell_type': 'markdown',
         'source': '# Header'},

        {'cell_type': 'markdown',
         'source': 'A paragraph.'},

        {'cell_type': 'markdown',
         'source': 'Python code:'},

        {'cell_type': 'code',
         'input': 'print("Hello world!")',
         'output': '"Hello world!"'},

        {'cell_type': 'markdown',
         'source': 'JavaScript code:'},

        {'cell_type': 'markdown',
         'source': '```javascript\nconsole.log("Hello world!");\n```'}
    ]

    # Read the Markdown file.
    reader = MarkdownReader()
    for cell, expected_cell in zip(reader.read(contents), expected_cells):
        assert cell == expected_cell

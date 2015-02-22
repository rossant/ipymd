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
    with open(_test_file_path('markdown.md'), 'r') as f:
        contents = f.read()

    # Read the Markdown file.
    reader = MarkdownReader()
    for cell in reader.read(contents):
        assert cell is None

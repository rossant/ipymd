# -*- coding: utf-8 -*-

"""Test notebook parser and reader."""

#------------------------------------------------------------------------------
# Imports
#------------------------------------------------------------------------------

from ..utils import _test_file_path, _exec_test_file
from ..notebook import NotebookReader, _open_ipynb


#------------------------------------------------------------------------------
# Test notebook reader and writer
#------------------------------------------------------------------------------

def test_notebook_reader():
    # Open a Markdown test file.
    ipynb = _open_ipynb(_test_file_path('notebook_simple.ipynb'))

    if ipynb['nbformat'] != 4:
        raise RuntimeError("Only nbformat v4 is supported for now.")

    nb_cells = ipynb['cells']

    # Convert ipynb to ipymd cells.
    reader = NotebookReader()
    cells = [cell for cell in reader.read(nb_cells)]

    # Read the expected cells.
    expected_cells = _exec_test_file('markdown_simple.py')

    # Compare.
    assert cells == expected_cells

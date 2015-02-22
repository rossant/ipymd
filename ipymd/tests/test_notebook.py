# -*- coding: utf-8 -*-

"""Test notebook parser and reader."""

#------------------------------------------------------------------------------
# Imports
#------------------------------------------------------------------------------

from ..utils import _test_file_path, _exec_test_file
from ..notebook import (NotebookReader, _open_ipynb, _compare_notebooks,
                        ipynb_to_ipymd_cells,
                        ipymd_cells_to_ipynb)


#------------------------------------------------------------------------------
# Test utility functions
#------------------------------------------------------------------------------

def _load_test_notebook():
    """Load a test notebook."""
    ipynb = _open_ipynb(_test_file_path('notebook_simple.ipynb'))
    if ipynb['nbformat'] != 4:
        raise RuntimeError("Only nbformat v4 is supported for now.")
    return ipynb['cells']


#------------------------------------------------------------------------------
# Test notebook reader and writer
#------------------------------------------------------------------------------

def test_notebook_reader():
    nb_cells = _load_test_notebook()

    # Convert ipynb to ipymd cells.
    cells = ipynb_to_ipymd_cells(nb_cells)

    # Read the expected cells.
    expected_cells = _exec_test_file('markdown_simple.py')

    # Compare.
    assert cells == expected_cells


def test_notebook_writer():

    cells = _exec_test_file('markdown_simple.py')
    nb_cells = ipymd_cells_to_ipynb(cells)

    expected_nb_cells = _load_test_notebook()

    # Compare.
    assert _compare_notebooks(nb_cells, expected_nb_cells)

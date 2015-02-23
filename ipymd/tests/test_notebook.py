# -*- coding: utf-8 -*-

"""Test notebook parser and reader."""

#------------------------------------------------------------------------------
# Imports
#------------------------------------------------------------------------------

from ..utils import _test_file_path, _exec_test_file
from ..notebook import (NotebookReader, _open_ipynb, _compare_notebooks,
                        ipynb_to_ipymd_cells,
                        ipymd_cells_to_ipynb,
                        _create_ipynb)


#------------------------------------------------------------------------------
# Test utility functions
#------------------------------------------------------------------------------

def _load_test_notebook():
    """Load a test notebook."""
    ipynb = _open_ipynb(_test_file_path('ex1.ipynb'))
    if ipynb['nbformat'] != 4:
        raise RuntimeError("Only nbformat v4 is supported for now.")
    return ipynb


#------------------------------------------------------------------------------
# Test notebook reader and writer
#------------------------------------------------------------------------------

def test_notebook_reader():

    # Load the test notebook.
    nb_cells = _load_test_notebook()['cells']

    # Convert ipynb to ipymd cells.
    cells = ipynb_to_ipymd_cells(nb_cells)

    # Read the expected cells.
    expected_cells = _exec_test_file('ex1.py')

    # Compare.
    assert cells == expected_cells


def test_notebook_writer():

    # Load the test ipymd cells.
    cells = _exec_test_file('ex1.py')

    # Convert to notebook.
    nb_cells = ipymd_cells_to_ipynb(cells)

    # Read the expected notebook cells.
    expected_nb_cells = _load_test_notebook()['cells']

    # Compare.
    assert _compare_notebooks(nb_cells, expected_nb_cells)


def test_create_ipynb():
    nb_cells = _exec_test_file('ex1.py')
    nb = _create_ipynb(nb_cells)
    assert nb['nbformat'] == 4

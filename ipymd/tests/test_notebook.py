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

def _load_test_notebook(basename):
    """Load a test notebook."""
    ipynb = _open_ipynb(_test_file_path(basename + '.ipynb'))
    if ipynb['nbformat'] != 4:
        raise RuntimeError("Only nbformat v4 is supported for now.")
    return ipynb


#------------------------------------------------------------------------------
# Test notebook reader and writer
#------------------------------------------------------------------------------

def _test_notebook_reader(basename):

    # Load the test notebook.
    nb_cells = _load_test_notebook(basename)['cells']

    # Convert ipynb to ipymd cells.
    cells = ipynb_to_ipymd_cells(nb_cells)

    # Read the expected cells.
    expected_cells = _exec_test_file(basename + '.py')

    # Compare.
    assert cells == expected_cells


def _test_notebook_writer(basename):

    # Load the test ipymd cells.
    cells = _exec_test_file(basename + '.py')

    # Convert to notebook.
    nb_cells = ipymd_cells_to_ipynb(cells)

    # Read the expected notebook cells.
    expected_nb_cells = _load_test_notebook(basename)['cells']

    # Compare.
    assert _compare_notebooks(nb_cells, expected_nb_cells)


def _test_create_ipynb(basename):
    nb_cells = _exec_test_file(basename + '.py')
    nb = _create_ipynb(nb_cells)
    assert nb['nbformat'] == 4


def test_notebook_reader():
    _test_notebook_reader('ex1')


def test_notebook_writer():
    _test_notebook_writer('ex1')


def test_create_ipynb():
    _test_create_ipynb('ex1')

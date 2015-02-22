# -*- coding: utf-8 -*-

"""Test scripts."""

#------------------------------------------------------------------------------
# Imports
#------------------------------------------------------------------------------

from ..notebook import _compare_notebooks
from ..scripts import nb_to_markdown, markdown_to_nb
from ..utils import _test_file_path, _exec_test_file, _read_test_file, _diff
from .test_notebook import _load_test_notebook


#------------------------------------------------------------------------------
# Test nb/markdown conversion functions
#------------------------------------------------------------------------------

def test_nb_to_markdown():
    nb = _load_test_notebook()
    md = nb_to_markdown(nb)

    # Check the result.
    md_expected = _read_test_file('markdown_simple.md')
    assert(_diff(md, md_expected) == '')

    # Check involution.
    nb_bis = markdown_to_nb(md)
    assert _compare_notebooks(nb['cells'], nb_bis['cells'])


def test_markdown_to_nb():
    md = _read_test_file('markdown_simple.md')
    nb = markdown_to_nb(md)

    # Check the result.
    nb_expected = _load_test_notebook()
    assert _compare_notebooks(nb['cells'], nb_expected['cells'])

    # Check involution.
    md_bis = nb_to_markdown(nb)
    assert(_diff(md, md_bis) == '')

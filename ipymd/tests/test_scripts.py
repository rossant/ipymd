# -*- coding: utf-8 -*-

"""Test scripts."""

#------------------------------------------------------------------------------
# Imports
#------------------------------------------------------------------------------

from ..notebook import _compare_notebooks
from ..scripts import nb_to_markdown, markdown_to_nb
from .test_notebook import _load_test_notebook


#------------------------------------------------------------------------------
# Test nb/markdown conversion functions
#------------------------------------------------------------------------------

def test_nb_to_markdown():
    nb = _load_test_notebook()
    md = nb_to_markdown(nb)

    nb_bis = markdown_to_nb(md)
    assert _compare_notebooks(nb['cells'], nb_bis['cells'])

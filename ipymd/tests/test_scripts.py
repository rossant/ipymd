# -*- coding: utf-8 -*-

"""Test scripts."""

#------------------------------------------------------------------------------
# Imports
#------------------------------------------------------------------------------

import os.path as op
import shutil

from ..notebook import _compare_notebooks
from ..scripts import nb_to_markdown, markdown_to_nb, _cli
from ..utils import _test_file_path, _exec_test_file, _read_test_file, _diff
from ..tempdir import TemporaryDirectory
from .test_notebook import _load_test_notebook


#------------------------------------------------------------------------------
# Test nb/markdown conversion functions
#------------------------------------------------------------------------------

def _test_nb_to_markdown(basename):
    nb = _load_test_notebook(basename)
    md = nb_to_markdown(nb)

    # Check the result.
    md_expected = _read_test_file(basename + '.md')
    assert(_diff(md, md_expected) == '')

    # Check involution.
    nb_bis = markdown_to_nb(md)
    assert _compare_notebooks(nb['cells'], nb_bis['cells'])


def _test_markdown_to_nb(basename):
    md = _read_test_file(basename + '.md')
    nb = markdown_to_nb(md)

    # Check the result.
    nb_expected = _load_test_notebook(basename)
    assert _compare_notebooks(nb['cells'], nb_expected['cells'])

    # Check involution.
    md_bis = nb_to_markdown(nb)
    assert(_diff(md, md_bis) == '')


def test_nb_to_markdown():
    _test_nb_to_markdown('ex1')


def test_markdown_to_nb():
    _test_markdown_to_nb('ex1')


#------------------------------------------------------------------------------
# Test CLI conversion tool
#------------------------------------------------------------------------------

def test_cli():
    basename = 'ex1'
    with TemporaryDirectory() as tempdir:
        # Copy some Markdown file to the temporary directory.
        md_orig = _test_file_path(basename + '.md')
        md_temp = op.join(tempdir, basename + '.md')
        shutil.copy(md_orig, md_temp)

        # Launch the CLI conversion tool.
        _cli(md_temp, convert_from='md')
        # TODO: more tests
        assert op.exists(op.join(tempdir, basename + '.ipynb'))

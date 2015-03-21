# -*- coding: utf-8 -*-

"""Test scripts."""

#------------------------------------------------------------------------------
# Imports
#------------------------------------------------------------------------------

import os.path as op
import shutil

from ..scripts import _cli, _common_root
from ...formats.tests._utils import _test_file_path
from ...utils.tempdir import TemporaryDirectory


#------------------------------------------------------------------------------
# Test utility functions
#------------------------------------------------------------------------------

def test_common_root():
    assert not _common_root([])
    assert _common_root(['a', 'b'])
    root = op.dirname(op.realpath(__file__))
    if not root.endswith('/'):
        root = root + '/'
    assert _common_root([op.join(root, 'a'),
                         op.join(root, 'b')]) == root
    assert (_common_root([op.join(root, '../tests/a'),
                          op.join(root, '../tests/b')]) == root)


#------------------------------------------------------------------------------
# Test CLI conversion tool
#------------------------------------------------------------------------------

def test_cli():
    basename = 'ex1'
    with TemporaryDirectory() as tempdir:
        # Copy some Markdown file to the temporary directory.
        md_orig = _test_file_path(basename, 'markdown')
        md_temp = op.join(tempdir, basename + '.md')
        shutil.copy(md_orig, md_temp)

        # Launch the CLI conversion tool.
        _cli(md_temp, from_='markdown', to='notebook')
        # TODO: more tests
        assert op.exists(op.join(tempdir, basename + '.ipynb'))

# -*- coding: utf-8 -*-

"""Test scripts."""

#------------------------------------------------------------------------------
# Imports
#------------------------------------------------------------------------------

import os
import os.path as op
import shutil

from ..scripts import convert_files, _common_root
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

def test_convert_files():
    basename = 'ex1'
    with TemporaryDirectory() as tempdir:

        # Copy some Markdown file to the temporary directory.
        md_orig = _test_file_path(basename, 'markdown')
        md_temp = op.join(tempdir, basename + '.md')
        shutil.copy(md_orig, md_temp)

        # Launch the CLI conversion tool.
        convert_files(md_temp, from_='markdown', to='notebook')

        # TODO: more tests
        assert op.exists(op.join(tempdir, basename + '.ipynb'))


def test_output_folder():
    with TemporaryDirectory() as tempdir:

        # Copy some Markdown file to the temporary directory.
        #
        # tempdir
        # |- ex1.md
        # |- subfolder/ex1.md
        md_orig = _test_file_path('ex1', 'markdown')
        md_temp_0 = op.join(tempdir, 'ex1.md')
        md_temp_1 = op.join(tempdir, 'subfolder', 'ex1.md')

        os.mkdir(op.join(tempdir, 'subfolder'))
        shutil.copy(md_orig, md_temp_0)
        shutil.copy(md_orig, md_temp_1)

        # Launch the CLI conversion tool.
        convert_files([md_temp_0, md_temp_1], from_='markdown', to='notebook',
                      output_folder=op.join(tempdir, 'output'))

        assert op.exists(op.join(tempdir, 'output/ex1.ipynb'))
        assert op.exists(op.join(tempdir, 'output/subfolder/ex1.ipynb'))

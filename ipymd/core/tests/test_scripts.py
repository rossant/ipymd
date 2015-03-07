# -*- coding: utf-8 -*-

"""Test scripts."""

#------------------------------------------------------------------------------
# Imports
#------------------------------------------------------------------------------

import os.path as op
import shutil

from ..scripts import _cli
from ...formats.tests._utils import _test_file_path
from ...utils.tempdir import TemporaryDirectory


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

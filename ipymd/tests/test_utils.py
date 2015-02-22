# -*- coding: utf-8 -*-

"""Test utils."""

#------------------------------------------------------------------------------
# Imports
#------------------------------------------------------------------------------

import os.path as op
from ..utils import _test_file_path, _exec_test_file


#------------------------------------------------------------------------------
# Test Markdown parser
#------------------------------------------------------------------------------

def test_file_path():
    filename = 'markdown.md'
    assert op.exists(_test_file_path(filename))


def test_exec_test_file():
    filename = 'markdown_simple.py'
    assert isinstance(_exec_test_file(filename), list)

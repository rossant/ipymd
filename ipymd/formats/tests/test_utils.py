# -*- coding: utf-8 -*-

"""Test utils."""

#------------------------------------------------------------------------------
# Imports
#------------------------------------------------------------------------------

import os.path as op
from ._utils import _test_file_path, _exec_test_file


#------------------------------------------------------------------------------
# Test Markdown parser
#------------------------------------------------------------------------------

def test_file_path():
    filename = 'ex1'
    assert op.exists(_test_file_path(filename, 'markdown'))


def test_exec_test_file():
    filename = 'ex1'
    assert isinstance(_exec_test_file(filename), list)

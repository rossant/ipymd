# -*- coding: utf-8 -*-

"""Test tempdir."""

#------------------------------------------------------------------------------
# Imports
#------------------------------------------------------------------------------

from ..tempdir import TemporaryDirectory


#------------------------------------------------------------------------------
# Tests
#------------------------------------------------------------------------------

def test_temporary_directory():
    with TemporaryDirectory() as temporary_directory:
        assert temporary_directory is not None

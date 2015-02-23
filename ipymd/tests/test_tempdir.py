# -*- coding: utf-8 -*-

"""Tests of HDF5 routines."""

#------------------------------------------------------------------------------
# Imports
#------------------------------------------------------------------------------

import numpy as np

from ..tempdir import TemporaryDirectory


#------------------------------------------------------------------------------
# Tests
#------------------------------------------------------------------------------

def test_temporary_directory():
    with TemporaryDirectory() as temporary_directory:
        assert temporary_directory is not None

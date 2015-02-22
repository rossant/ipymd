# -*- coding: utf-8 -*-

"""Utils"""

#------------------------------------------------------------------------------
# Imports
#------------------------------------------------------------------------------

import os
import os.path as op


#------------------------------------------------------------------------------
# Utils
#------------------------------------------------------------------------------

def _script_dir():
    return op.dirname(op.realpath(__file__))


def _test_file_path(filename):
    """Return the full path to an example filename in the 'notebooks'
    directory."""
    return op.realpath(op.join(_script_dir(), '../notebooks', filename))

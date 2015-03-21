# -*- coding: utf-8 -*-

"""Python utility functions."""


# -----------------------------------------------------------------------------
# Imports
# -----------------------------------------------------------------------------

import ast

from ..ext.six import string_types


# -----------------------------------------------------------------------------
# Utility functions
# -----------------------------------------------------------------------------

def _is_python(source):
    """Return whether a string contains valid Python code."""
    try:
        ast.parse(source)
        return True
    except SyntaxError:
        return False


class PythonFilter(object):
    def __init__(self, ipymd_skip=None):
        self._ipymd_skip = ipymd_skip

    def filter(self, code):
        code = code.rstrip()
        if self._ipymd_skip:
            return '\n'.join(line for line in code.splitlines()
                             if 'ipymd-skip' not in line)
        else:
            return code

    def __call__(self, code):
        return self.filter(code)

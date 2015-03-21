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
    def __init__(self):
        pass

    def filter(self, code):
        return '\n'.join(line for line in code.splitlines()
                         if 'ipymd-skip' not in line)

    def __call__(self, code):
        return self.filter(code)

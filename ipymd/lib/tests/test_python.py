# -*- coding: utf-8 -*-

"""Test Python routines."""

# -----------------------------------------------------------------------------
# Imports
# -----------------------------------------------------------------------------

from ..python import _is_python, PythonFilter


# -----------------------------------------------------------------------------
# Test Python
# -----------------------------------------------------------------------------

def test_python():
    assert _is_python("print('Hello world!')")
    assert not _is_python("Hello world!")


def test_python_filter():
    filter = PythonFilter()
    assert filter('a\nb # ipymd-skip\nc\n') == 'a\nb # ipymd-skip\nc'

    filter = PythonFilter(ipymd_skip=True)
    assert filter('a\nb # ipymd-skip\nc\n') == 'a\nc'

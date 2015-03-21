# -*- coding: utf-8 -*-

"""Test Python parser and reader."""

#------------------------------------------------------------------------------
# Imports
#------------------------------------------------------------------------------

from ...core.format_manager import format_manager, convert
from ...utils.utils import _remove_output, _diff, _show_outputs
from ._utils import (_test_reader, _test_writer,
                     _exec_test_file, _read_test_file)
from ..python import _split_python


#------------------------------------------------------------------------------
# Test Python utility functions
#------------------------------------------------------------------------------

def test_split_python():
    python = '\n'.join((
        'a',
        'b = "1"',
        '',
        "c = '''",
        'd',
        '',
        '',
        'e',
        "'''",
        '',
        '# comment',
    ))
    chunks = _split_python(python)
    assert len(chunks) == 3


def test_python_headers():
    cells = _exec_test_file('ex2')

    # Keep H1.
    converted = convert(cells, to='python',
                        to_kwargs={'keep_markdown': 'h1'})
    assert converted.startswith('# # Test notebook\n\n# some code in python')
    assert len(converted.splitlines()) == 30

    # Keep H2, H3.
    converted = convert(cells, to='python',
                        to_kwargs={'keep_markdown': 'h2,h3'})
    assert not converted.startswith('# # Test notebook\n\n# some code')
    assert len(converted.splitlines()) == 30

    # Keep all headers.
    converted = convert(cells, to='python',
                        to_kwargs={'keep_markdown': 'headers'})
    assert converted.startswith('# # Test notebook\n\n# some code in python')
    assert len(converted.splitlines()) == 32

    # Keep all Markdown.
    converted = convert(cells, to='python',
                        to_kwargs={'keep_markdown': 'all'})
    assert len(converted.splitlines()) == 72

    # Keep no Markdown.
    converted = convert(cells, to='python',
                        to_kwargs={'keep_markdown': False})
    assert len(converted.splitlines()) == 28


def test_commented_python():
    python = '\n'.join((
        '# # Title',
        '',
        '# pass',
        '# Hello world.',
        '',
        '# # commented Python code should not be converted to Markdown',
        '# print(1)',
        '# 3+3',
        '# if False:',
        '#     exit(1/0)',
        '',
        '# Text again.',
    ))
    cells = convert(python, from_='python')
    assert [cell['cell_type'] for cell in cells] == ['markdown',
                                                     'markdown',
                                                     'code',
                                                     'markdown',
                                                     ]


#------------------------------------------------------------------------------
# Test Python parser
#------------------------------------------------------------------------------

def _test_python_reader(basename):
    """Check that (test cells) and (test contents ==> cells) are the same."""
    converted, expected = _test_reader(basename, 'python')
    assert _remove_output(converted) == _remove_output(expected)


def _test_python_writer(basename):
    """Check that (test contents) and (test cells ==> contents) are the same.
    """
    converted, expected = _test_writer(basename, 'python')
    assert _diff(converted, expected) == ''


def _test_python_python(basename):
    """Check that the double conversion is the identity."""

    contents = _read_test_file(basename, 'python')
    cells = convert(contents, from_='python')
    converted = convert(cells, to='python')

    assert _diff(contents, converted) == ''


def test_python_reader():
    _test_python_reader('ex1')
    _test_python_reader('ex2')


def test_python_writer():
    _test_python_writer('ex1')
    _test_python_writer('ex2')


def test_python_python():
    _test_python_python('ex1')
    _test_python_python('ex2')

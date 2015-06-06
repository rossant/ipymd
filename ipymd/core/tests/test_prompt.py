# -*- coding: utf-8 -*-

"""Test prompt manager."""

#------------------------------------------------------------------------------
# Imports
#------------------------------------------------------------------------------

from ..prompt import (SimplePromptManager,
                      IPythonPromptManager,
                      PythonPromptManager,
                      _template_to_regex,
                      _starts_with_regex,
                      )
from ...utils.utils import _show_outputs


#------------------------------------------------------------------------------
# Prompt manager tests
#------------------------------------------------------------------------------

def test_utils():
    template = 'In [{n}]: '
    regex = _template_to_regex(template)
    assert regex == r'In \[\d+\]\: '

    assert not _starts_with_regex('In []: ', regex)
    assert not _starts_with_regex('In [s]: ', regex)
    assert not _starts_with_regex('Out [1]: ', regex)
    assert _starts_with_regex('In [1]: ', regex)
    assert _starts_with_regex('In [23]: ', regex)
    assert _starts_with_regex('In [23]: print()\n', regex)


class MockPromptManager(SimplePromptManager):
    input_prompt_template = '> '
    output_prompt_template = ''


def test_simple_split():
    pm = MockPromptManager()
    assert pm.is_input('> 1')
    assert not pm.is_input('>1')
    assert not pm.is_input('1')


def _test(prompt_manager_cls, in_out, text):
    input, output = in_out

    # Cell => text.
    pm = prompt_manager_cls()
    text_pm = pm.from_cell(input, output)
    assert text_pm == text

    # Text => cell.
    input_pm, output_pm = pm.to_cell(text)
    assert input_pm == input

    assert output_pm == output


def test_simple_split():
    pm = MockPromptManager()
    assert pm.split_input_output('> 1\n> 2\n3\n4') == (['> 1', '> 2'],
                                                       ['3', '4'])


def test_simple_prompt_manager():
    input, output = 'print("1")\nprint("2")', '1\n2'
    text = '> print("1")\n> print("2")\n1\n2'

    _test(MockPromptManager, (input, output), text)


def test_ipython_split():
    pm = IPythonPromptManager()
    text = 'In [1]: print("1")\n        print("2")\nOut [1]: 1\n         2'

    assert pm.split_input_output(text) == (['In [1]: print("1")',
                                            '        print("2")'],
                                           ['Out [1]: 1',
                                            '         2'])


def test_ipython_prompt_manager():
    input, output = 'print("1")\nprint("2")', '1\n2'
    text = 'In [1]: print("1")\n        print("2")\nOut[1]: 1\n        2'

    _test(IPythonPromptManager, (input, output), text)


def test_python_split():
    pm = PythonPromptManager()
    text = '>>> print("1")\n>>> print("2")\n>>> def f():\n...     pass\n1\n2'

    assert pm.split_input_output(text) == (['>>> print("1")',
                                            '>>> print("2")',
                                            '>>> def f():',
                                            '...     pass'],
                                           ['1',
                                            '2'])


def test_python_prompt_manager():
    input, output = 'print("1")\nprint("2")\ndef f():\n    pass', '1\n2'
    text = '>>> print("1")\n>>> print("2")\n>>> def f():\n...     pass\n1\n2'

    _test(PythonPromptManager, (input, output), text)

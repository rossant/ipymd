# -*- coding: utf-8 -*-

"""Test prompt manager."""

#------------------------------------------------------------------------------
# Imports
#------------------------------------------------------------------------------

from ..prompt import (SimplePromptManager,
                      IPythonPromptManager,
                      PythonPromptManager,
                      )
from ...formats.tests._utils import _show_outputs


#------------------------------------------------------------------------------
# Prompt manager tests
#------------------------------------------------------------------------------

def _test(prompt_manager_cls, in_out, text):
    (input, output) = in_out

    pm = prompt_manager_cls()
    text_pm = pm.from_cell(input, output)
    assert text_pm == text

    # input_pm, output_pm = pm.to_cell(text)
    # assert input_pm == input
    # assert output_pm == output


def test_simple_prompt_manager():

    class MockPromptManager(SimplePromptManager):
        input_prompt_template = '> '
        output_prompt_template = ''

    input, output = 'print("1")\nprint("2")', '1\n2'
    text = '> print("1")\n> print("2")\n1\n2'

    _test(MockPromptManager, (input, output), text)


def test_ipython_prompt_manager():

    input, output = 'print("1")\nprint("2")', '1\n2'
    text = 'In [1]: print("1")\n        print("2")\nOut [1]: 1\n         2'

    _test(IPythonPromptManager, (input, output), text)


def test_python_prompt_manager():

    input, output = 'print("1")\nprint("2")\ndef f():\n    pass', '1\n2'
    text = '>>> print("1")\n>>> print("2")\n>>> def f():\n...     pass\n1\n2'

    _test(PythonPromptManager, (input, output), text)

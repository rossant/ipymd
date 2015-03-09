# -*- coding: utf-8 -*-

"""Test prompt manager."""

#------------------------------------------------------------------------------
# Imports
#------------------------------------------------------------------------------

from ..prompt import SimplePromptManager, IPythonPromptManager
from ...formats.tests._utils import _show_outputs


#------------------------------------------------------------------------------
# Prompt manager tests
#------------------------------------------------------------------------------

def test_simple_prompt_manager():

    class MockPromptManager(SimplePromptManager):
        input_prompt_template = '> '
        output_prompt_template = ''

    input, output = 'print("1")\nprint("2")', '1\n2'
    text_e = '> print("1")\n> print("2")\n1\n2'

    pm = MockPromptManager()
    text = pm.from_cell(input, output)

    assert text == text_e


def test_ipython_prompt_manager():

    input, output = 'print("1")\nprint("2")', '1\n2'
    text_e = 'In [1]: print("1")\n        print("2")\nOut [1]: 1\n         2'

    pm = IPythonPromptManager()
    text = pm.from_cell(input, output)

    assert text == text_e

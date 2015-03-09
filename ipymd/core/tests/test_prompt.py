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

def test_base_prompt_manager():

    class MockPromptManager(SimplePromptManager):
        input_prompt_template = '> '
        output_prompt_template = ''

    text_e = '> print("1")\n> print("2")\n1\n2'
    input_e, output_e = 'print("1")\nprint("2")', '1\n2'

    pm = MockPromptManager()
    text = pm.from_cell(input_e, output_e)

    assert text == text_e

# -*- coding: utf-8 -*-

"""Test prompt manager."""

#------------------------------------------------------------------------------
# Imports
#------------------------------------------------------------------------------

from ..prompt import BasePromptManager, IPythonPromptManager


#------------------------------------------------------------------------------
# Prompt manager tests
#------------------------------------------------------------------------------

def test_base_prompt_manager():
    pm = BasePromptManager()
    assert pm

# -*- coding: utf-8 -*-

"""Test base lexer."""

# -----------------------------------------------------------------------------
# Imports
# -----------------------------------------------------------------------------

import re

from ..base_lexer import BaseLexer, BaseGrammar


# -----------------------------------------------------------------------------
# Tests
# -----------------------------------------------------------------------------

class Grammar(BaseGrammar):
    word = re.compile(r'^\w+')
    space = re.compile(r'^\s+')


class Lexer(BaseLexer):
    grammar_class = Grammar
    default_rules = ['word', 'space']
    words = []

    def parse_word(self, m):
        self.words.append(m.group(0))

    def parse_space(self, m):
        pass


def test_base_lexer():
    lexer = Lexer()
    text = "hello world"
    lexer.read(text)
    assert lexer.words == ['hello', 'world']

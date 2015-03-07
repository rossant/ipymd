# -*- coding: utf-8 -*-

"""Base lexer.

The code has been adapted from the mistune library:

    mistune
    https://github.com/lepture/mistune/

    The fastest markdown parser in pure Python with renderer feature.
    :copyright: (c) 2014 - 2015 by Hsiaoming Yang.

"""


# -----------------------------------------------------------------------------
# Base lexer
# -----------------------------------------------------------------------------

class BaseLexer(object):
    grammar_class = None
    default_rules = []
    renderer_cls = None

    def __init__(self, renderer=None, grammar=None, rules=None):
        if grammar is None:
            grammar = self.grammar_class()
        if rules is None:
            rules = self.default_rules
        if renderer is None:
            renderer = self.renderer_cls()
        self.grammar = grammar
        self.rules = rules
        self.renderer = renderer

    def manipulate(self, text, rules):
        for key in rules:
            rule = getattr(self.grammar, key)
            m = rule.match(text)
            if not m:
                continue
            getattr(self, 'parse_%s' % key)(m)
            return m
        return False

    def preprocess(self, text):
        return text.rstrip('\n')

    def read(self, text, rules=None):
        if rules is None:
            rules = self.rules
        text = self.preprocess(text)
        while text:
            m = self.manipulate(text, rules)
            if m is not False:
                text = text[len(m.group(0)):]
                continue
            if text:
                raise RuntimeError('Infinite loop at: %s' % text)

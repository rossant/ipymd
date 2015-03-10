# -*- coding: utf-8 -*-

"""Base lexer.

The code has been adapted from the mistune library:

    mistune
    https://github.com/lepture/mistune/

    The fastest markdown parser in pure Python with renderer feature.
    :copyright: (c) 2014 - 2015 by Hsiaoming Yang.

"""

# -----------------------------------------------------------------------------
# Imports
# -----------------------------------------------------------------------------

from functools import partial


# -----------------------------------------------------------------------------
# Base lexer
# -----------------------------------------------------------------------------

class BaseGrammar(object):
    pass


class BaseRenderer(object):
    def __init__(self, verbose=False):
        self._verbose = verbose
        self._handler = self._process

    def handler(self, func):
        self._handler = func

    def _process(self, name, *args, **kwargs):
        if self._verbose:
            sargs = ', '.join(args)
            skwargs = ', '.join('{k}={v}'.format(k=k, v=v)
                                for k, v in kwargs.items())
            print(name, sargs, skwargs)

    def __getattr__(self, name):
        return partial(self._handler, name)


class BaseLexer(object):
    grammar_class = BaseGrammar
    default_rules = []
    renderer_class = BaseRenderer

    def __init__(self, renderer=None, grammar=None, rules=None):
        if grammar is None:
            grammar = self.grammar_class()
        if rules is None:
            rules = self.default_rules
        if renderer is None:
            renderer = self.renderer_class()
        self.grammar = grammar
        self.rules = rules
        self.renderer = renderer

    def manipulate(self, text, rules):
        for key in rules:
            rule = getattr(self.grammar, key)
            m = rule.match(text)
            if not m:
                continue
            out = getattr(self, 'parse_%s' % key)(m)
            return m, out
        return False, None

    def preprocess(self, text):
        return text.rstrip('\n')

    def read(self, text, rules=None):
        if rules is None:
            rules = self.rules
        text = self.preprocess(text)
        tokens = []
        while text:
            m, out = self.manipulate(text, rules)
            if out is None:
                tokens.append(m)
            else:
                tokens.append(out)
            if m is not False:
                text = text[len(m.group(0)):]
                continue
            if text:
                raise RuntimeError('Infinite loop at: %s' % text)
        return tokens

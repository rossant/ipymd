# -*- coding: utf-8 -*-

"""Test Markdown lexers."""

# -----------------------------------------------------------------------------
# Imports
# -----------------------------------------------------------------------------

import re

from ..base_lexer import BaseRenderer
from ..markdown import BlockLexer, InlineLexer, BaseMarkdownRenderer


# -----------------------------------------------------------------------------
# Tests Markdown inline lexer
# -----------------------------------------------------------------------------

class InlineRenderer(BaseRenderer):
    def __init__(self):
        super(InlineRenderer, self).__init__(verbose=False)
        self.output = []

    def text(self, text):
        self.output.append(text)

    def emphasis(self, text):
        self.output.append('<i>')
        self.text(text)
        self.output.append('</i>')

    def double_emphasis(self, text):
        self.output.append('<b>')
        self.text(text)
        self.output.append('</b>')

    def linebreak(self):
        self.output.append('<br>')


def test_inline_lexer():
    renderer = InlineRenderer()
    text = ("First *paragraph*.\n**Second** line.")
    lexer = InlineLexer(renderer=renderer)
    lexer.read(text)
    expected = ['First ',
                '<i>', 'paragraph', '</i>',
                '.',
                '<br>',
                '<b>', 'Second', '</b>',
                ' line.'
                ]
    assert renderer.output == expected


# -----------------------------------------------------------------------------
# Tests Markdown block lexer
# -----------------------------------------------------------------------------

class BlockRenderer(BaseRenderer):
    def __init__(self):
        super(BlockRenderer, self).__init__(verbose=False)
        self.output = []

    def paragraph_start(self):
        self.output.append('<p>')

    def paragraph_end(self):
        self.output.append('</p>')

    def list_start(self, ordered=None):
        self._ordered = ordered
        if self._ordered:
            self.output.append('<ol>')
        else:
            self.output.append('<ul>')

    def list_end(self):
        if self._ordered:
            self.output.append('</ol>')
        else:
            self.output.append('</ul>')
        self._ordered = None

    def list_item_start(self):
        self.output.append('<li>')

    def list_item_end(self):
        self.output.append('</li>')

    def newline(self):
        self.output.append('\n')

    def block_text(self, text):
        self.output.append(text)

    def block_code(self, text, lang=None):
        self.output.append('<code>')
        self.output.append(text)
        self.output.append('</code>')


def test_block_lexer():
    renderer = BlockRenderer()
    text = ("First *paragraph*.\n**Second** line.\n\n"
            "* Item 1.\n* Item 2.\n\n```\ncode\n```\n\n"
            "1. First.\n2. Second.\n\n"
            "End.")
    lexer = BlockLexer(renderer=renderer)
    lexer.read(text)
    expected = ['<p>', 'First *paragraph*.\n**Second** line.', '</p>',

                '<ul>',
                '<li>', 'Item 1.', '</li>',
                '<li>', 'Item 2.', '</li>',
                '</ul>',

                '<code>', 'code', '</code>',

                '<ol>',
                '<li>', 'First.', '</li>',
                '<li>', 'Second.', '</li>',
                '</ol>',

                '<p>', 'End.', '</p>',
                ]
    assert renderer.output == expected

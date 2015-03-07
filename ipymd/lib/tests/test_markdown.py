# -*- coding: utf-8 -*-

"""Test Markdown lexers."""

# -----------------------------------------------------------------------------
# Imports
# -----------------------------------------------------------------------------

import re
from pprint import pprint

from ..base_lexer import BaseRenderer
from ..markdown import BlockLexer, InlineLexer


# -----------------------------------------------------------------------------
# Test renderers
# -----------------------------------------------------------------------------

class BlockRenderer(BaseRenderer):
    def __init__(self):
        super(BlockRenderer, self).__init__()
        self.output = []

    def paragraph(self, text):
        self.output.append('<p>')
        self.text(text)
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

    def text(self, text):
        self.output.append(text)

    def block_code(self, text, lang=None):
        self.output.append('<code>')
        self.output.append(text)
        self.output.append('</code>')


class InlineRenderer(BaseRenderer):
    def __init__(self, output=None):
        super(InlineRenderer, self).__init__()
        if output is None:
            output = []
        self.output = output

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

    def codespan(self, text):
        self.output.append('<codespan>')
        self.text(text)
        self.output.append('</codespan>')

    def linebreak(self):
        self.output.append('<br>')


class FullBlockRenderer(BlockRenderer):
    def text(self, text):
        inline_renderer = InlineRenderer(self.output)
        inline_lexer = InlineLexer(renderer=inline_renderer)
        inline_lexer.read(text)


# -----------------------------------------------------------------------------
# Tests Markdown block lexer
# -----------------------------------------------------------------------------

_TEST_TEXT = ("First *paragraph*.\n**Second** line.\n\n"
              "* Item 1.\n* Item 2.\n\n```\ncode\n```\n\n"
              "1. First.\n2. Second.\n\n"
              "End.")


def test_block_lexer():
    renderer = BlockRenderer()
    text = _TEST_TEXT
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


# -----------------------------------------------------------------------------
# Tests Markdown inline lexer
# -----------------------------------------------------------------------------

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
# Tests full Markdown lexer
# -----------------------------------------------------------------------------

def test_full_lexer():
    renderer = FullBlockRenderer()
    lexer = BlockLexer(renderer=renderer)
    text = _TEST_TEXT
    lexer.read(text)
    expected = ['<p>',
                'First ', '<i>', 'paragraph', '</i>', '.',
                '<br>',
                '<b>', 'Second', '</b>', ' line.',
                '</p>',

                '<ul>',
                '<li>', 'Item 1.', '</li>',
                '<li>', 'Item 2.', '</li>',
                '</ul>',

                '<code>', 'code', '</code>',

                '<ol>',
                '<li>', 'First.', '</li>',
                '<li>', 'Second.', '</li>',
                '</ol>',

                '<p>', 'End.', '</p>']
    assert renderer.output == expected

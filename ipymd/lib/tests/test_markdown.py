# -*- coding: utf-8 -*-

"""Test Markdown lexers."""

# -----------------------------------------------------------------------------
# Imports
# -----------------------------------------------------------------------------

import re
from pprint import pprint

from ..base_lexer import BaseRenderer
from ..markdown import BlockLexer, InlineLexer, MarkdownWriter
from ...utils.utils import _show_outputs


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

    def block_quote_start(self):
        self.output.append('<quote>')

    def block_quote_end(self):
        self.output.append('</quote>')


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

    def link(self, link, title, text):
        self.output.append('<a>')
        self.text(text)
        self.output('</a>')


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
              "> End.\n")


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

                '<quote>', '<p>', 'End.', '</p>', '</quote>'
                ]
    assert renderer.output == expected


def test_block_lexer_list():
    renderer = BlockRenderer()
    text = "* 1\n* 2\n  * 2.1\n* 3"
    lexer = BlockLexer(renderer=renderer)
    lexer.read(text)
    expected = ['<ul>',
                '<li>', '1', '</li>',
                '<li>', '2',
                '<ul>',
                '<li>', '2.1', '</li>',
                '</ul>',
                '</li>',
                '<li>', '3', '</li>',
                '</ul>',
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


def test_brackets():
    renderer = InlineRenderer()
    text = ("Some [1] reference.")
    lexer = InlineLexer(renderer=renderer)
    lexer.read(text)
    expected = ['Some ',
                '[1] reference.',
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

                '<quote>', '<p>', 'End.', '</p>', '</quote>'
                ]
    assert renderer.output == expected


# -----------------------------------------------------------------------------
# Test Markdown writer
# -----------------------------------------------------------------------------

def test_markdown_writer_newline():
    w = MarkdownWriter()
    w.text('Hello.')
    w.ensure_newline(1)
    w.text('Hello.\n')
    w.ensure_newline(1)
    w.text('Hello.\n\n')
    w.ensure_newline(1)
    w.text('Hello.\n\n\n')
    w.ensure_newline(2)
    w.text('End')

    expected = ('Hello.\n' * 4) + '\nEnd\n'

    assert w.contents == expected


def test_markdown_writer():
    w = MarkdownWriter()

    expected = '\n'.join(("# First chapter",
                          "",
                          "**Hello** *world*!",
                          "How are you? Some `code`.",
                          "",
                          "> Good, and you?",
                          "> End of citation.",
                          "",
                          "* Item **1**.",
                          "* Item 2.",
                          "",
                          "1. 1",
                          "  * 1.1",
                          "    * 1.1.1",
                          "2. 2",
                          "",
                          "```",
                          "print(\"Hello world!\")",
                          "```",
                          "",
                          ("Go to [google](http://www.google.com). "
                           "And here is an image for you:"),
                          "",
                          "![Some image](my_image.png)\n"))

    w.heading('First chapter', 1)
    w.newline()

    w.bold('Hello')
    w.text(' ')
    w.italic('world')
    w.text('!')
    w.linebreak()
    w.text('How are you? Some ')
    w.inline_code('code')
    w.text('.')
    w.newline()

    w.quote_start()
    w.text('Good, and you?')
    w.linebreak()
    w.text('End of citation.')
    w.quote_end()
    w.newline()

    w.list_item('Item ')
    w.bold('1')
    w.text('.')
    w.linebreak()
    w.list_item('Item 2.')
    w.newline()

    w.numbered_list_item('1')
    w.linebreak()
    w.list_item('1.1', level=1)
    w.linebreak()
    w.list_item('1.1.1', level=2)
    w.linebreak()
    w.numbered_list_item('2')
    w.newline()

    w.code_start()
    w.text('print("Hello world!")')
    w.code_end()
    w.newline()

    w.text('Go to ')
    w.link('google', 'http://www.google.com')
    w.text('. And here is an image for you:')
    w.newline()

    w.image('Some image', 'my_image.png')

    _show_outputs(w.contents, expected)
    assert w.contents == expected

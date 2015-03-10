# -*- coding: utf-8 -*-

"""Test OpenDocument routines."""


# -----------------------------------------------------------------------------
# Imports
# -----------------------------------------------------------------------------

from ..base_lexer import BaseRenderer
from ..markdown import BlockLexer
from ..opendocument import (ODFDocument, ODFRenderer, BaseODFReader,
                            odf_to_markdown,
                            markdown_to_odf,
                            _merge_text)
from ...utils.utils import _show_outputs


# -----------------------------------------------------------------------------
# Test ODFDocument
# -----------------------------------------------------------------------------

def test_merge_text():
    items = [{'tag': 'span', 'text': '1'},
             {'tag': 'span', 'text': '2'},
             {'tag': 'span', 'text': '-', 'style': 'bold'},
             {'tag': 'span', 'text': '3'},
             {'tag': 'span', 'text': '4'}]
    merged = _merge_text(*items)
    assert merged == [{'tag': 'span', 'text': '12'},
                      {'tag': 'span', 'text': '-', 'style': 'bold'},
                      {'tag': 'span', 'text': '34'}]


def _example_opendocument():
    doc = ODFDocument()

    doc.heading("The title", 1)

    with doc.paragraph():
        doc.text("Some text. ")
        doc.bold("This is bold.")

    with doc.list():
        with doc.list_item():
            with doc.paragraph():
                doc.text("Item 1.")
        with doc.list_item():
            with doc.paragraph():
                doc.text("Item 2.")
            with doc.list():
                with doc.list_item():
                    with doc.paragraph():
                        doc.text("Item 2.1. This is ")
                        doc.inline_code("code")
                        doc.text(". Oh, and here is a link: ")
                        doc.link("http://google.com")
                        doc.text(".")
                with doc.list_item():
                    with doc.paragraph():
                        doc.text("Item 2.2.")
        with doc.list_item():
            with doc.paragraph():
                doc.text("Item 3.")

    doc.start_quote()
    with doc.paragraph():
        doc.text("This is a citation.")
        doc.linebreak()
        doc.text("End.")
    doc.end_quote()

    with doc.numbered_list():
        with doc.list_item():
            with doc.paragraph():
                doc.text("Item 1.")
        with doc.list_item():
            with doc.paragraph():
                doc.text("Item 2.")

    doc.code("def f():\n"
             "    print('Hello world!')\n")

    with doc.paragraph():
        doc.text("End.")

    return doc


def _example_markdown():
    return '\n'.join(('# The title',
                      '',
                      'Some text. **This is bold.**',
                      '',
                      '* Item 1.',
                      '* Item 2.',
                      ('  * Item 2.1. This is `code`. '
                       'Oh, and here is a link: http://google.com.'),
                      '  * Item 2.2.',
                      '* Item 3.',
                      '',
                      '> This is a citation.',
                      '> End.',
                      '',
                      '1. Item 1.',
                      '2. Item 2.',
                      '',
                      '```',
                      'def f():',
                      '    print(\'Hello world!\')',
                      '```',
                      '',
                      'End.',
                      ''))


def test_odf_document():
    doc = _example_opendocument()
    doc.show_styles()


def test_odf_renderer():
    doc = ODFDocument()
    renderer = ODFRenderer(doc)
    block_lexer = BlockLexer(renderer=renderer)
    text = "Hello world!"
    block_lexer.read(text)


def test_odf_reader():
    doc = _example_opendocument()
    reader = BaseODFReader()

    _items = []

    @reader.handler
    def f(name, *args, **kwargs):
        _items.append(name)

    reader.read(doc)

    assert len(_items) == 64


# -----------------------------------------------------------------------------
# Test ODF <=> Markdown converter
# -----------------------------------------------------------------------------

def test_odf_markdown_converter():
    doc = _example_opendocument()
    md = _example_markdown()
    converted = odf_to_markdown(doc)

    assert md == converted


def test_markdown_odf_converter():
    doc = _example_opendocument()
    md = _example_markdown()
    converted = markdown_to_odf(md)

    assert doc == converted

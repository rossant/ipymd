# -*- coding: utf-8 -*-

"""Test OpenDocument routines."""


# -----------------------------------------------------------------------------
# Imports
# -----------------------------------------------------------------------------

from ..base_lexer import BaseRenderer
from ..markdown import BlockLexer
from ..opendocument import (ODFDocument, ODFRenderer, BaseODFReader,
                            odf_to_markdown)


# -----------------------------------------------------------------------------
# Test ODFDocument
# -----------------------------------------------------------------------------

def _example_document():
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

    doc.code("print('Hello world!')")

    return doc


def test_odf_document():
    doc = _example_document()
    doc.show_styles()


def test_odf_renderer():
    doc = ODFDocument()
    renderer = ODFRenderer(doc)
    block_lexer = BlockLexer(renderer=renderer)
    text = "Hello world!"
    block_lexer.read(text)


def test_odf_reader():
    doc = _example_document()
    reader = BaseODFReader()

    _items = []

    @reader.handler
    def f(name, *args, **kwargs):
        _items.append(name)

    reader.read(doc)

    assert len(_items) == 53


# -----------------------------------------------------------------------------
# Test ODF => Markdown converter
# -----------------------------------------------------------------------------

def test_odf_markdown_converter():
    doc = _example_document()
    md = odf_to_markdown(doc)
    print(md)
    assert md

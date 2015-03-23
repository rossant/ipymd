# -*- coding: utf-8 -*-

"""OpenDocument renderers."""


# -----------------------------------------------------------------------------
# Imports
# -----------------------------------------------------------------------------

from ..core.prompt import create_prompt
from ..lib.markdown import InlineLexer, BlockLexer, BaseRenderer
from ..lib.opendocument import (ODFDocument, ODFRenderer,
                                odf_to_markdown,
                                load_odf, save_odf)
from .markdown import MarkdownReader


# -----------------------------------------------------------------------------
# ODF renderers
# -----------------------------------------------------------------------------

class ODFReader(object):
    def read(self, contents):
        # contents is an ODFDocument.
        md = odf_to_markdown(contents)
        reader = MarkdownReader()
        return reader.read(md)


class ODFWriter(object):
    def __init__(self, prompt=None, odfdoc=None):
        self._odfdoc = odfdoc or ODFDocument()
        self._prompt = create_prompt(prompt)
        renderer = ODFRenderer(self._odfdoc)
        self._block_lexer = BlockLexer(renderer=renderer)

    def write(self, cell):
        if cell['cell_type'] == 'markdown':
            md = cell['source']
            # Convert the Markdown cell to ODF.
            self._block_lexer.read(md)
        elif cell['cell_type'] == 'code':
            # Add the code cell to ODF.
            source = self._prompt.from_cell(cell['input'], cell['output'])
            self._odfdoc.code(source)

    @property
    def contents(self):
        return self._odfdoc


ODF_FORMAT = dict(
    name='opendocument',
    reader=ODFReader,
    writer=ODFWriter,
    file_extension='.odt',
    load=load_odf,
    save=save_odf,
)

# -*- coding: utf-8 -*-

"""OpenDocument renderers."""


# -----------------------------------------------------------------------------
# Imports
# -----------------------------------------------------------------------------

from ..lib.markdown import InlineLexer, BlockLexer, BaseRenderer
from ..lib.opendocument import load, ODFDocument, ODFRenderer
from ..ext.six import text_type


# -----------------------------------------------------------------------------
# ODF renderers
# -----------------------------------------------------------------------------

def _add_prompt(code):
    # TODO
    return code


class ODFReader(object):
    def read(self, contents):
        # contents is an ODFDocument.
        # TODO: yield a list of ipymd cells
        return []


class ODFWriter(object):
    def __init__(self):
        self._doc = ODFDocument()

    def write(self, cell):
        if cell['cell_type'] == 'markdown':
            md = cell['source']
            # Convert the Markdown cell to ODF.
            renderer = ODFRenderer(self._doc)
            block_lexer = BlockLexer(renderer=renderer)
            block_lexer.read(md)
        elif cell['cell_type'] == 'code':
            # Add the code cell to ODF.
            input = _add_prompt(cell['input'].rstrip())
            output = cell['output'].rstrip()
            self._doc.code(input + '\n' + output)

    @property
    def contents(self):
        return self._doc


def load_odf(path):
    # HACK: work around a bug in odfpy: make sure the path string is unicode.
    path = text_type(path)
    doc = load(path)
    return ODFDocument(doc=doc)


def save_odf(path, contents):
    contents.save(path)


ODF_FORMAT = dict(
    name='opendocument',
    reader=ODFReader,
    writer=ODFWriter,
    file_extension='.odt',
    load=load_odf,
    save=save_odf,
)

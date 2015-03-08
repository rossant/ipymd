# -*- coding: utf-8 -*-

"""OpenDocument renderers."""


# -----------------------------------------------------------------------------
# Imports
# -----------------------------------------------------------------------------

from ..lib.markdown import InlineLexer, BlockLexer, BaseRenderer
from ..lib.opendocument import load, ODFDocument, ODFRenderer


# -----------------------------------------------------------------------------
# ODF renderers
# -----------------------------------------------------------------------------

class ODFReader(object):
    def read(self, contents):
        # conents is an ODFDocument.
        pass


class ODFWriter(object):
    def __init__(self):
        self._doc = ODFDocument()

    def write(self, cell):
        # TODO
        pass

    @property
    def contents(self):
        return self._doc


def load_odf(path):
    doc = load(path)
    return ODFDocument(doc=doc)


def save_odf(path, contents):
    contents.save(path)


ODF_FORMAT = dict(
    name='odf',
    reader=ODFReader,
    writer=ODFWriter,
    file_extension='.odt',
    load=load_odf,
    save=save_odf,
)

# -*- coding: utf-8 -*-

"""Python reader and writer."""

#------------------------------------------------------------------------------
# Imports
#------------------------------------------------------------------------------

import re
import ast
from collections import OrderedDict

from ..lib.base_lexer import BaseGrammar, BaseLexer
from ..lib.markdown import MarkdownFilter
from ..lib.python import _is_python
from ..ext.six import StringIO
from ..utils.utils import _ensure_string, _preprocess


#------------------------------------------------------------------------------
# Python reader and writer
#------------------------------------------------------------------------------

class PythonSplitGrammar(BaseGrammar):
    """Grammar used to split Python code into chunks while not cutting
    long Python strings."""

    _triple_quotes = "'''"
    _triple_doublequotes = '"""'
    _triple = _triple_quotes + '|' + _triple_doublequotes

    # '''text''' or """text""".
    text_var = re.compile(r"^({0})((?!{0}).|\n)*?\1".format(_triple))

    # Two new lines followed by non-space
    newline = re.compile(r'^[\n]{2,}(?=[^ ])')

    linebreak = re.compile(r'^\n+')
    other = re.compile(r'^(?!{0}).'.format(_triple))


class PythonSplitLexer(BaseLexer):
    """Lexer for splitting Python code into chunks."""

    grammar_class = PythonSplitGrammar
    default_rules = ['text_var', 'newline', 'linebreak', 'other']

    def __init__(self):
        super(PythonSplitLexer, self).__init__()
        self._chunks = ['']

    @property
    def current(self):
        if not self._chunks:
            return None
        else:
            return self._chunks[-1]

    @property
    def chunks(self):
        return [chunk for chunk in self._chunks if chunk]

    @current.setter
    def current(self, value):
        self._chunks[-1] = value

    def new_chunk(self):
        self._chunks.append('')

    def append(self, text):
        self.current += text

    def parse_newline(self, m):
        self.new_chunk()

    def parse_linebreak(self, m):
        self.append(m.group(0))

    def parse_text_var(self, m):
        self.append(m.group(0))

    def parse_other(self, m):
        self.append(m.group(0))


def _split_python(python):
    """Split Python source into chunks.

    Chunks are separated by at least two return lines. The break must not
    be followed by a space. Also, long Python strings spanning several lines
    are not splitted.

    """
    python = _preprocess(python)
    if not python:
        return []
    lexer = PythonSplitLexer()
    lexer.read(python)
    return lexer.chunks


def _is_chunk_markdown(source):
    """Return whether a chunk contains Markdown contents."""
    lines = source.splitlines()
    if all(line.startswith('# ') for line in lines):
        # The chunk is a Markdown *unless* it is commented Python code.
        source = '\n'.join(line[2:] for line in lines
                           if not line[2:].startswith('#'))  # skip headers
        if not source:
            return True
        # Try to parse the chunk: if it fails, it is Markdown, otherwise,
        # it is Python.
        return not _is_python(source)
    return False


def _remove_hash(source):
    """Remove the leading '#' of every line in the source."""
    return '\n'.join(line[2:].rstrip() for line in source.splitlines())


def _add_hash(source):
    """Add a leading hash '#' at the beginning of every line in the source."""
    source = '\n'.join('# ' + line.rstrip()
                       for line in source.splitlines())
    return source


class PythonReader(object):
    """Python reader."""
    def read(self, python):
        chunks = _split_python(python)
        for chunk in chunks:
            if _is_chunk_markdown(chunk):
                yield self._markdown_cell(_remove_hash(chunk))
            else:
                yield self._code_cell(chunk)

    def _code_cell(self, source):
        return {'cell_type': 'code',
                'input': source,
                'output': None}

    def _markdown_cell(self, source):
        return {'cell_type': 'markdown',
                'source': source}


class PythonWriter(object):
    """Python writer."""
    def __init__(self, keep_markdown=None):
        self._output = StringIO()
        self._markdown_filter = MarkdownFilter(keep_markdown)

    def _new_paragraph(self):
        self._output.write('\n\n')

    def append_comments(self, source):
        source = source.rstrip()
        # Filter Markdown contents.
        source = self._markdown_filter(source)
        # Skip empty cells.
        if not source:
            return
        comments = _add_hash(source)
        self._output.write(comments)
        self._new_paragraph()

    def append_code(self, input):
        self._output.write(input)
        self._new_paragraph()

    def write(self, cell):
        if cell['cell_type'] == 'markdown':
            self.append_comments(cell['source'])
        elif cell['cell_type'] == 'code':
            self.append_code(cell['input'])

    @property
    def contents(self):
        return self._output.getvalue().rstrip() + '\n'  # end of file \n

    def close(self):
        self._output.close()

    def __del__(self):
        self.close()


PYTHON_FORMAT = dict(
    name='python',
    reader=PythonReader,
    writer=PythonWriter,
    file_extension='.py',
    file_type='text',
)

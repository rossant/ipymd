# -*- coding: utf-8 -*-

"""Python reader and writer."""

#------------------------------------------------------------------------------
# Imports
#------------------------------------------------------------------------------

import re
import ast
from collections import OrderedDict

from ..lib.base_lexer import BaseGrammar, BaseLexer
from ..ext.six import StringIO
from ..utils.utils import _ensure_string, _preprocess


#------------------------------------------------------------------------------
# Python reader and writer
#------------------------------------------------------------------------------

class PythonSplitGrammar(BaseGrammar):
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
    grammar_class = PythonSplitGrammar
    default_rules = ['text_var', 'newline', 'linebreak', 'other']
    chunks = ['']

    @property
    def current(self):
        if not self.chunks:
            return None
        else:
            return self.chunks[-1]

    @current.setter
    def current(self, value):
        self.chunks[-1] = value

    def new_chunk(self):
        self.chunks.append('')

    def append(self, text):
        self.current += text

    def parse_newline(self, m):
        # print("parse_newline")
        self.new_chunk()

    def parse_linebreak(self, m):
        # print("parse_linebreak")
        self.append(m.group(0))

    def parse_text_var(self, m):
        print("parse_text_var")
        self.append(m.group(0))

    def parse_other(self, m):
        # print("parse_other")
        self.append(m.group(0))


def _split_python(python):
    """Split Python source into chunks.

    Chunks are separated by at least two return lines. The break must not
    be followed by a space.

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
        try:
            ast.parse(source)
            return False
        except SyntaxError:
            return True
    return False


def _remove_hash(source):
    """Remove the leading '#' of every line in the source."""
    return '\n'.join(line[2:].rstrip() for line in source.splitlines())


def _add_hash(source):
    """Add a leading hash '#' at the beginning of every line in the source."""
    source = '\n'.join('# ' + line.rstrip()
                       for line in source.splitlines())
    return source


def _replace_header_filter(filter):
    return {'h1': '# ',
            'h2': '## ',
            'h3': '### ',
            'h4': '#### ',
            'h5': '##### ',
            'h6': '###### ',
            }[filter]


def _filter_markdown(source, filters):
    """Only keep some Markdown headers from a Markdown string."""
    lines = source.splitlines()
    # Filters is a list of 'hN' strings where 1 <= N <= 6.
    headers = [_replace_header_filter(filter) for filter in filters]
    lines = [line for line in lines if line.startswith(tuple(headers))]
    return '\n'.join(lines)


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
    """Python writer.

    Parameters
    ----------

    keep_markdown : str | None or False
        What to keep from Markdown cells. Can be:

        * None or False: don't keep Markdown contents
        * 'all': keep all Markdown contents
        * 'headers': just keep Markdown headers
        * 'h1,h3': just keep headers of level 1 and 3 (can be any combination)

    """

    def __init__(self, keep_markdown='all'):
        self._output = StringIO()
        if keep_markdown == 'headers':
            keep_markdown = 'h1,h2,h3,h4,h5,h6'
        self._keep_markdown = keep_markdown

    def _new_paragraph(self):
        self._output.write('\n\n')

    def append_comments(self, source):
        source = source.rstrip()

        # Skip Markdown cell.
        if not self._keep_markdown:
            return
        # Only keep some Markdown headers if keep_markdown is not 'all'.
        elif self._keep_markdown != 'all':
            to_keep = self._keep_markdown.split(',')
            source = _filter_markdown(source, to_keep)

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

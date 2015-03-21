# -*- coding: utf-8 -*-

"""Python reader and writer."""

#------------------------------------------------------------------------------
# Imports
#------------------------------------------------------------------------------

import re
from collections import OrderedDict

from ..ext.six import StringIO
from ..utils.utils import _ensure_string, _preprocess


#------------------------------------------------------------------------------
# Python reader and writer
#------------------------------------------------------------------------------

def _split_python(python):
    """Split Python source into chunks.

    Chunks are separated by at least two return lines. The break must not
    be followed by a space.

    """
    python = _preprocess(python)
    cells = re.split(r'[\n]{2,}(?=[^ ])', python)
    return cells


def _is_chunk_comment(source):
    """Return whether a chunk is a comment."""
    if all(line.startswith('# ') for line in source.splitlines()):
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
            if _is_chunk_comment(chunk):
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

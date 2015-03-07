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
    return all(line.startswith('# ') for line in source.splitlines())


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
    """Python writer."""

    def __init__(self):
        self._output = StringIO()

    def _new_paragraph(self):
        self._output.write('\n\n')

    def append_comments(self, source):
        comments = source.rstrip()
        comments = _add_hash(comments)
        self._output.write(comments)

    def append_code(self, input):
        self._output.write(input)

    def write(self, cell):
        if cell['cell_type'] == 'markdown':
            self.append_comments(cell['source'])
        elif cell['cell_type'] == 'code':
            self.append_code(cell['input'])
        self._new_paragraph()

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

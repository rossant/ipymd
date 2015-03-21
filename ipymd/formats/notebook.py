# -*- coding: utf-8 -*-

"""Notebook reader and writer."""

#------------------------------------------------------------------------------
# Imports
#------------------------------------------------------------------------------

import json

import IPython.nbformat as nbf
from IPython.nbformat.v4.nbbase import validate

from ..lib.markdown import MarkdownFilter
from ..lib.python import PythonFilter
from ..ext.six import string_types
from ..utils.utils import _ensure_string


#------------------------------------------------------------------------------
# Utility functions
#------------------------------------------------------------------------------

def _cell_input(cell):
    """Return the input of an ipynb cell."""
    return _ensure_string(cell.get('source', []))


def _cell_output(cell):
    """Return the output of an ipynb cell."""
    outputs = cell.get('outputs', [])
    # Add stdout.
    stdout = ('\n'.join(_ensure_string(output.get('text', ''))
                        for output in outputs)).rstrip()
    # Add text output.
    text_outputs = []
    for output in outputs:
        out = output.get('data', {}).get('text/plain', [])
        out = _ensure_string(out)
        # HACK: skip <matplotlib ...> outputs.
        if out.startswith('<matplotlib'):
            continue
        text_outputs.append(out)
    return stdout + '\n'.join(text_outputs).rstrip()


def _compare_notebook_cells(cell_0, cell_1):
    return all((cell_0['cell_type'] == cell_1['cell_type'],
                _cell_input(cell_0) == _cell_input(cell_1),
                _cell_output(cell_0) == _cell_output(cell_1)))


def _compare_notebooks(nb_0, nb_1):
    return all(_compare_notebook_cells(cell_0, cell_1)
               for cell_0, cell_1 in zip(nb_0['cells'], nb_1['cells']))


#------------------------------------------------------------------------------
# Notebook reader
#------------------------------------------------------------------------------

class NotebookReader(object):
    """Reader for notebook cells.

    nbformat v4 only."""
    def read(self, nb):
        assert nb['nbformat'] >= 4
        for cell in nb['cells']:
            ipymd_cell = {}
            ctype = cell['cell_type']
            ipymd_cell['cell_type'] = ctype
            if ctype == 'code':
                ipymd_cell['input'] = _cell_input(cell)
                ipymd_cell['output'] = _cell_output(cell)
            elif ctype == 'markdown':
                ipymd_cell['source'] = _ensure_string(cell['source'])
            else:
                continue
            yield ipymd_cell


#------------------------------------------------------------------------------
# Notebook writer
#------------------------------------------------------------------------------

class NotebookWriter(object):
    def __init__(self, keep_markdown=None, ipymd_skip=False):
        self._nb = nbf.v4.new_notebook()
        self._count = 1
        self._markdown_filter = MarkdownFilter(keep_markdown)
        self._code_filter = PythonFilter(ipymd_skip=ipymd_skip)

    def append_markdown(self, source):
        # Filter Markdown contents.
        source = self._markdown_filter(source)
        if not source:
            return
        self._nb['cells'].append(nbf.v4.new_markdown_cell(source))

    def append_code(self, input, output=None, image=None):
        input = self._code_filter(input)
        cell = nbf.v4.new_code_cell(input, execution_count=self._count)
        if output:
            cell.outputs.append(nbf.v4.new_output('execute_result',
                                {'text/plain': output},
                                execution_count=self._count,
                                metadata={},
                                ))
        if image:
            # TODO
            raise NotImplementedError("Output images not implemented yet.")
        self._nb['cells'].append(cell)
        self._count += 1

    def write(self, cell):
        if cell['cell_type'] == 'markdown':
            self.append_markdown(cell['source'])
        elif cell['cell_type'] == 'code':
            self.append_code(cell['input'], cell['output'])

    @property
    def contents(self):
        validate(self._nb)
        return self._nb


NOTEBOOK_FORMAT = dict(
    name='notebook',
    reader=NotebookReader,
    writer=NotebookWriter,
    file_extension='.ipynb',
    file_type='json',
)

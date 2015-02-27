# -*- coding: utf-8 -*-

"""Notebook reader and writer."""

#------------------------------------------------------------------------------
# Imports
#------------------------------------------------------------------------------

import json

import IPython.nbformat as nbf

from .six import string_types
from .utils import _ensure_string


#------------------------------------------------------------------------------
# Utility functions
#------------------------------------------------------------------------------


def _read_nb(contents_or_path):
    """Load a notebook contents from a dict or a path to a .ipynb file."""
    if isinstance(contents_or_path, string_types):
        with open(contents_or_path, "r") as f:
            return json.load(f)
    else:
        return contents_or_path


def _write_nb(file, contents):
    """Write a notebook to a JSON ipynb file."""
    with open(file, 'w') as f:
        return json.dump(contents, f, indent=2)


def _create_ipynb(cells):
    """Create a new ipynb model from a list of ipynb cells."""
    nb = nbf.v4.new_notebook()
    nb['cells'] = cells
    return nb


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
               for cell_0, cell_1 in zip(nb_0, nb_1))


#------------------------------------------------------------------------------
# Notebook reader
#------------------------------------------------------------------------------

class NotebookReader(object):
    """Reader for notebook cells.

    nbformat v4 only."""
    def read(self, nb_cells):
        for cell in nb_cells:
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
    def __init__(self):
        self._nb = nbf.v4.new_notebook()
        self._count = 1

    def append_markdown(self, source):
        self._nb['cells'].append(nbf.v4.new_markdown_cell(source))

    def append_code(self, input, output=None, image=None):
        cell = nbf.v4.new_code_cell(input)
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
        return self._nb

    def save(self, filename):
        with open(filename, 'w') as f:
            nbf.write(self._nb, f)


#------------------------------------------------------------------------------
# Helper notebook conversion functions
#------------------------------------------------------------------------------

# TODO: delete those and replace with convert()
def ipynb_to_ipymd_cells(nb_cells):
    """Convert a list of notebook cells to a list of ipymd cells."""
    return list(NotebookReader().read(nb_cells))


def ipymd_cells_to_ipynb(ipymd_cells):
    """Convert a list of ipymd cells to a list of notebook cells."""
    writer = NotebookWriter()
    for cell in ipymd_cells:
        writer.write(cell)
    return writer.contents['cells']

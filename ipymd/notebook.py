# -*- coding: utf-8 -*-

"""Notebook reader and writer."""

#------------------------------------------------------------------------------
# Imports
#------------------------------------------------------------------------------

import json

from .six import string_types


#------------------------------------------------------------------------------
# Utility functions
#------------------------------------------------------------------------------

def _open_ipynb(contents_or_path):
    """Load a notebook contents from a dict or a path to a .ipynb file."""
    if isinstance(contents_or_path, string_types):
        with open(contents_or_path, "r") as f:
            return json.load(f)
    else:
        return contents_or_path


def _ensure_string(source):
    """Ensure a source is a string."""
    if isinstance(source, list):
        input = '\n'.join([line.rstrip() for line in source])
    else:
        input = source
    return input.rstrip()


def _cell_input(cell):
    """Return the input of an ipynb cell."""
    return _ensure_string(cell.get('source', []))


def _cell_output(cell):
    """Return the output of an ipynb cell."""
    outputs = cell.get('outputs', [])
    # Add stdout.
    output = ('\n'.join(_ensure_string(output.get('text', ''))
                        for output in outputs)).rstrip()
    # Add text output.
    output += ('\n'.join(_ensure_string(output.get('data', {}).
                                        get('text/plain', []))
                         for output in outputs)).rstrip()
    return output


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
                ipymd_cell['source'] = cell['source']
            else:
                continue
            yield ipymd_cell


#------------------------------------------------------------------------------
# Notebook writer
#------------------------------------------------------------------------------

class NotebookWriter(object):
    def append_markdown(self, source):
        pass

    def append_code(self, input, output=None, image=None):
        pass

    def contents(self):
        pass

    def save(self, filename):
        pass


#------------------------------------------------------------------------------
# Helper notebook conversion functions
#------------------------------------------------------------------------------

def ipynb_to_ipymd_cells(nb_cells):
    """Convert a list of notebook cells to a list of ipymd cells."""
    return list(NotebookReader().read(nb_cells))


def ipymd_cells_to_ipynb(ipymd_cells):
    pass

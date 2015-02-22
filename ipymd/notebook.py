# -*- coding: utf-8 -*-

"""Notebook reader and writer."""

#------------------------------------------------------------------------------
# Imports
#------------------------------------------------------------------------------


#------------------------------------------------------------------------------
# Utility functions
#------------------------------------------------------------------------------

def _ensure_string(source):
    """Ensure a source is a string."""
    if isinstance(source, list):
        input = '\n'.join([line.rstrip() for line in source])
    else:
        input = source
    return input.rstrip()


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
    def read(self, ipynb_cells):
        for ipynb_cell in ipynb_cells:
            # TODO: cell type?
            cell = {'cell_type': None}
            output = _cell_output(ipynb_cell)
            assert output
            yield cell


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

def ipynb_to_ipymd_cells(ipynb_cells):
    pass


def ipymd_cells_to_ipynb(ipymd_cells):
    pass

# -*- coding: utf-8 -*-

"""Notebook reader and writer."""

#------------------------------------------------------------------------------
# Imports
#------------------------------------------------------------------------------


#------------------------------------------------------------------------------
# Notebook reader
#------------------------------------------------------------------------------

class NotebookReader(object):
    def read(self, ipynb_cells):
        pass


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

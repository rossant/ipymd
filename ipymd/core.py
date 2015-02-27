# -*- coding: utf-8 -*-

"""Core conversion functions."""

#------------------------------------------------------------------------------
# Imports
#------------------------------------------------------------------------------

import argparse
import re
import os
import os.path as op
import glob
import json

from .six import string_types
from . import formats


#------------------------------------------------------------------------------
# Format manager
#------------------------------------------------------------------------------

class FormatManager(object):
    def __init__(self):
        self._formats = {}

    def register(self, name=None, **kwargs):
        # print("Registering '{0:s}' format.".format(name))
        self._formats[name] = kwargs

    def formats(self):
        return sorted(self._formats)

    def _check_format(self, name):
        if name not in self._formats:
            raise ValueError("This format '{0:s}' has not ".format(name) +
                             "been registered.")

    def file_extension(self, name):
        return self._formats[name]['file_extension']

    def file_type(self, name):
        return self._formats[name]['file_type']

    def create_reader(self, name, *args, **kwargs):
        self._check_format(name)
        return self._formats[name]['reader'](*args, **kwargs)

    def create_writer(self, name, *args, **kwargs):
        self._check_format(name)
        return self._formats[name]['writer'](*args, **kwargs)


_FORMAT_MANAGER = None


def format_manager():
    """Return a FormatManager singleton instance."""
    global _FORMAT_MANAGER
    if _FORMAT_MANAGER is None:
        # Discover the formats and register them.
        _FORMAT_MANAGER = FormatManager()
        # TODO: improve this. Currently, a module in ipymd/formats needs
        # to have a SOMETHING_FORMAT global dictionary. It would be
        # better to expose an on_load(format_manager) function.
        for name in dir(formats):
            if re.match(r'^[^\n]+\_FORMAT$', name):
                _FORMAT_MANAGER.register(**getattr(formats, name))
    return _FORMAT_MANAGER


#------------------------------------------------------------------------------
# Conversion function
#------------------------------------------------------------------------------

def convert(contents,
            from_=None,
            to=None,
            from_kwargs=None,
            to_kwargs=None,
            ):

    if from_kwargs is None:
        from_kwargs = {}
    if to_kwargs is None:
        to_kwargs = {}

    reader = (format_manager().create_reader(from_, **from_kwargs)
              if from_ is not None else None)

    writer = (format_manager().create_writer(to, **to_kwargs)
              if to is not None else None)

    if reader is not None:
        # Convert from the source format to ipymd cells.
        cells = [cell for cell in reader.read(contents)]
    else:
        # If no reader is specified, 'contents' is assumed to already be
        # a list of ipymd cells.
        cells = contents

    if writer is not None:
        # Convert from ipymd cells to the target format.
        for cell in cells:
            writer.write(cell)
        return writer.contents
    else:
        # If no writer is specified, the output is supposed to be
        # a list of ipymd cells.
        return cells

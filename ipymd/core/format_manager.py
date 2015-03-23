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

from ..ext.six import string_types
from ..utils.utils import _read_text, _read_json, _write_text, _write_json
from .. import formats


#------------------------------------------------------------------------------
# Format manager
#------------------------------------------------------------------------------

def _is_path(s):
    """Return whether an object is a path."""
    if isinstance(s, string_types):
        return op.exists(s)
    else:
        return False


class FormatManager(object):
    def __init__(self):
        self._formats = {}

    def register(self, name=None, **kwargs):
        """Register a format.

        Parameters
        ----------

        reader : class
            A class that implements read(contents) which yield ipymd cells.
        writer : class
            A class that implements write(cell) and contents.
        file_extension : str
            The file extension with the leading dot, like '.md'
        file_type : 'text' or 'json'
            The type of the file format.
        load : function
            a custom `contents = load(path)` function if no file type
               is specified.
        save : function
            a custom `save(path, contents)` function if no file type
               is specified.

        """
        assert name is not None
        self._formats[name] = kwargs

    def unregister(self, name):
        """Unregister a format."""
        del self._formats[name]

    @property
    def formats(self):
        """Return the sorted list of registered formats."""
        return sorted(self._formats)

    def _check_format(self, name):
        if name not in self._formats:
            raise ValueError("This format '{0:s}' has not ".format(name) +
                             "been registered.")

    def file_extension(self, name):
        """Return the file extension of a registered format."""
        return self._formats[name]['file_extension']

    def format_from_extension(self, extension):
        """Find a format from its extension."""
        formats = [name
                   for name, format in self._formats.items()
                   if format.get('file_extension', None) == extension]
        if len(formats) == 0:
            return None
        elif len(formats) == 2:
            raise RuntimeError("Several extensions are registered with "
                               "that extension; please specify the format "
                               "explicitly.")
        else:
            return formats[0]

    def file_type(self, name):
        """Return the file type of a registered format."""
        return self._formats[name].get('file_type', None)

    def load(self, file, name=None):
        """Load a file. The format name can be specified explicitly or
        inferred from the file extension."""
        if name is None:
            name = self.format_from_extension(op.splitext(file)[1])
        file_format = self.file_type(name)
        if file_format == 'text':
            return _read_text(file)
        elif file_format == 'json':
            return _read_json(file)
        else:
            load_function = self._formats[name].get('load', None)
            if load_function is None:
                raise IOError("The format must declare a file type or "
                              "load/save functions.")
            return load_function(file)

    def save(self, file, contents, name=None, overwrite=False):
        """Save contents into a file. The format name can be specified
        explicitly or inferred from the file extension."""
        if name is None:
            name = self.format_from_extension(op.splitext(file)[1])
        file_format = self.file_type(name)
        if file_format == 'text':
            _write_text(file, contents)
        elif file_format == 'json':
            _write_json(file, contents)
        else:
            write_function = self._formats[name].get('save', None)
            if write_function is None:
                raise IOError("The format must declare a file type or "
                              "load/save functions.")
            if op.exists(file) and not overwrite:
                print("The file already exists, please use overwrite=True.")
                return
            write_function(file, contents)

    def create_reader(self, name, *args, **kwargs):
        """Create a new reader instance for a given format."""
        self._check_format(name)
        return self._formats[name]['reader'](*args, **kwargs)

    def create_writer(self, name, *args, **kwargs):
        """Create a new writer instance for a given format."""
        self._check_format(name)
        return self._formats[name]['writer'](*args, **kwargs)

    def convert(self,
                contents_or_path,
                from_=None,
                to=None,
                reader=None,
                writer=None,
                from_kwargs=None,
                to_kwargs=None,
                ):
        """Convert contents between supported formats.

        Parameters
        ----------

        contents : str
            The contents to convert from.
        from_ : str or None
            The name of the source format. If None, this is the
            ipymd_cells format.
        to : str or None
            The name of the target format. If None, this is the
            ipymd_cells format.
        reader : a Reader instance or None
        writer : a Writer instance or None
        from_kwargs : dict
            Optional keyword arguments to pass to the reader instance.
        to_kwargs : dict
            Optional keyword arguments to pass to the writer instance.

        """

        # Load the file if 'contents_or_path' is a path.
        if _is_path(contents_or_path):
            contents = self.load(contents_or_path, from_)
        else:
            contents = contents_or_path

        if from_kwargs is None:
            from_kwargs = {}
        if to_kwargs is None:
            to_kwargs = {}

        if reader is None:
            reader = (self.create_reader(from_, **from_kwargs)
                      if from_ is not None else None)

        if writer is None:
            writer = (self.create_writer(to, **to_kwargs)
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


def convert(*args, **kwargs):
    """Alias for format_manager().convert()."""
    return format_manager().convert(*args, **kwargs)

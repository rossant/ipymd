# -*- coding: utf-8 -*-

"""Utils"""

#------------------------------------------------------------------------------
# Imports
#------------------------------------------------------------------------------

import os
import os.path as op
import json

from .six import exec_, string_types


#------------------------------------------------------------------------------
# Utils
#------------------------------------------------------------------------------

def _ensure_string(source):
    """Ensure a source is a string."""
    if isinstance(source, string_types):
        return source.rstrip()
    else:
        return '\n'.join([line.rstrip() for line in source]).rstrip()


#------------------------------------------------------------------------------
# Reading/writing files from/to disk
#------------------------------------------------------------------------------

def _read_json(file):
    """Read a JSON file."""
    with open(file, 'r') as f:
        return json.load(f)


def _write_json(file, contents):
    """Write a dict to a JSON file."""
    with open(file, 'w') as f:
        return json.dump(contents, f, indent=2)


def _read_text(file):
    """Read a Markdown file."""
    with open(file, 'r') as f:
        return f.read()


def _write_text(file, contents):
    """Write a Markdown file."""
    with open(file, 'w') as f:
        f.write(contents)

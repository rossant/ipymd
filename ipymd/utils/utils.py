# -*- coding: utf-8 -*-

"""Utils"""

#------------------------------------------------------------------------------
# Imports
#------------------------------------------------------------------------------

import os
import os.path as op
import re
import difflib
from pprint import pprint
import json

from ..ext.six import exec_, string_types


#------------------------------------------------------------------------------
# Utils
#------------------------------------------------------------------------------

def _rstrip_lines(source):
    if not isinstance(source, list):
        source = source.splitlines()
    return '\n'.join(line.rstrip() for line in source)


def _ensure_string(source):
    """Ensure a source is a string."""
    if isinstance(source, string_types):
        return source.rstrip()
    else:
        return _rstrip_lines(source)


def _preprocess(text, tab=4):
    """Normalize a text."""
    text = re.sub(r'\r\n|\r', '\n', text)
    text = text.replace('\t', ' ' * tab)
    text = text.replace('\u00a0', ' ')
    text = text.replace('\u2424', '\n')
    pattern = re.compile(r'^ +$', re.M)
    text = pattern.sub('', text)
    text = _rstrip_lines(text)
    return text


def _remove_output_cell(cell):
    """Remove the output of an ipymd cell."""
    cell = cell.copy()
    if cell['cell_type'] == 'code':
        cell['output'] = None
    return cell


def _remove_output(cells):
    """Remove all code outputs from a list of ipymd cells."""
    return [_remove_output_cell(cell) for cell in cells]


def _remove_code_lang_code(cell):
    if cell['cell_type'] == 'markdown':
        cell['source'] = re.sub(r'```[^\n]*', '```', cell['source'])
    return cell


def _remove_code_lang(cells):
    """Remove all lang in code cells."""
    return [_remove_code_lang_code(cell) for cell in cells]


def _remove_images(cells):
    """Remove markdown cells with images."""
    return [cell for cell in cells
            if not cell.get('source', '').startswith('![')]


def _flatten_links_cell(cell):
    if cell['cell_type'] == 'markdown':
        cell['source'] = re.sub(r'\[([^\]]+)\]\(([^\)]+)\)', r'\1 (\2)',
                                cell['source'])
    return cell


def _flatten_links(cells):
    """Replace hypertext links by simple URL text."""
    return [_flatten_links_cell(cell) for cell in cells]


def _diff_removed_lines(diff):
    return ''.join(x[2:] for x in diff if x.startswith('- '))


def _diff(text_0, text_1):
    """Return a diff between two strings."""
    diff = difflib.ndiff(text_0.splitlines(), text_1.splitlines())
    return _diff_removed_lines(diff)


def _show_outputs(*outputs):
    for output in outputs:
        print()
        print("-" * 30)
        pprint(output)


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

# -*- coding: utf-8 -*-

"""CLI scripts."""

#------------------------------------------------------------------------------
# Imports
#------------------------------------------------------------------------------

import argparse
import os
import os.path as op
import glob
import json

from .six import string_types
from .notebook import (ipynb_to_ipymd_cells, ipymd_cells_to_ipynb,
                       _create_ipynb, _read_nb, _write_nb)
from .markdown import (markdown_to_ipymd_cells, ipymd_cells_to_markdown,
                       _read_md, _write_md)
from .atlas import (AtlasReader, AtlasWriter,
                    atlas_to_ipymd_cells,
                    ipymd_cells_to_atlas)


#------------------------------------------------------------------------------
# Public conversion functions
#------------------------------------------------------------------------------

def nb_to_markdown(nb, writer=None):
    """Convert a notebook contents to a Markdown document."""
    # Only work for nbformat 4 for now.
    assert nb['nbformat'] >= 4
    nb_cells = nb['cells']
    ipymd_cells = ipynb_to_ipymd_cells(nb_cells)
    md = ipymd_cells_to_markdown(ipymd_cells, writer=writer)
    return md


def markdown_to_nb(contents, reader=None):
    """Convert a Markdown document to an ipynb model."""
    ipymd_cells = markdown_to_ipymd_cells(contents, reader=reader)
    nb_cells = ipymd_cells_to_ipynb(ipymd_cells)
    return _create_ipynb(nb_cells)


def nb_to_atlas(nb):
    """Convert a notebook contents to an Atlas document."""
    return nb_to_markdown(writer=AtlasWriter())


def atlas_to_nb(nb):
    """Convert an Atlas document to an ipynb model."""
    return markdown_to_nb(reader=AtlasReader())


def markdown_to_atlas(contents):
    """Convert a Markdown document to Atlas."""
    cells = atlas_to_ipymd_cells(contents)
    return ipymd_cells_to_markdown(cells)


def atlas_to_markdown(contents):
    """Convert an Atlas document to Markdown."""
    cells = ipymd_cells_to_atlas(contents)
    return atlas_to_ipymd_cells(cells)


#------------------------------------------------------------------------------
# Scripts
#------------------------------------------------------------------------------

def _flatten(l):
    return [item for sublist in l for item in sublist]


def _ensure_list(l):
    if isinstance(l, string_types):
        return [l]
    elif isinstance(l, list):
        return l
    else:
        raise RuntimeError("This should be a string or a list: "
                           "{0:s}.".format(str(l)))


def _to_skip(dirname):
    return op.basename(dirname).startswith('._/')


def _expand_dirs_to_files(files_or_dirs):
    files = []
    files_or_dirs = _ensure_list(files_or_dirs)
    for file_or_dir in files_or_dirs:
        if op.isdir(file_or_dir):
            # Skip dirnames starting with '.'
            if _to_skip(file_or_dir):
                continue
            # Recursively visit the directories and add the files.
            files.extend(_expand_dirs_to_files([op.join(file_or_dir, file)
                         for file in os.listdir(file_or_dir)]))
        elif '*' in file_or_dir:
            files.extend(glob.glob(file_or_dir))
        else:
            files.append(file_or_dir)
    return files


def _file_has_extension(file, extensions):
    if not isinstance(extensions, list):
        extensions = [extensions]
    return any(file.endswith(extension) for extension in extensions)


def _filter_files_by_extension(files, extensions):
    return [file for file in files if _file_has_extension(file, extensions)]


def _converted_filename(file, convert_from):
    base, ext = op.splitext(file)
    if convert_from == 'ipynb':
        convert_ext = '.md'
    elif convert_from == 'md':
        convert_ext = '.ipynb'
    return ''.join((base, convert_ext))


def _cli(files_or_dirs, overwrite=None, convert_from=None):
    # Find all files.
    files = _expand_dirs_to_files(files_or_dirs)

    # Filter as a function of --from.
    if convert_from == 'ipynb':
        files = _filter_files_by_extension(files, '.ipynb')
        convert = nb_to_markdown
        read = _read_nb
        write = _write_md
        # TODO: other conversions
    elif convert_from in ('md', 'markdown', 'atlas'):
        files = _filter_files_by_extension(files, '.md')
        if convert_from == 'atlas':
            convert = atlas_to_nb
        else:
            convert = markdown_to_nb
        read = _read_md
        write = _write_nb
    else:
        raise ValueError("'from' should be 'ipynb' or 'md'")

    for file in files:
        print("Converting {0:s}...".format(file))
        contents = read(file)
        converted = convert(contents)
        converted = contents
        file_to = _converted_filename(file, convert_from)
        if op.exists(file_to) and not overwrite:
            print("The file already exists, please use --overwrite.")
            continue
        else:
            write(file_to, converted)


def main():
    parser = argparse.ArgumentParser(description='Convert ipynb/md.')

    parser.add_argument('files_or_dirs', nargs='+',
                        help=('list of ipynb or md files or directories '
                              'to convert'))

    parser.add_argument('--from', dest='convert_from', required=True,
                        help='one of "md", "atlas", "ipynb"')

    parser.add_argument('--overwrite', dest='overwrite', action='store_true',
                        help=('overwrite target file if it exists '
                              '(false by default)'))

    # Parse the CLI arguments.
    args = parser.parse_args()
    files_or_dirs = args.files_or_dirs
    # md_type = args.type or 'markdown'
    overwrite = args.overwrite
    convert_from = args.convert_from

    _cli(files_or_dirs, overwrite=overwrite, convert_from=convert_from)


if __name__ == '__main__':
    main()

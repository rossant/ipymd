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
from .utils import _read_text, _read_json, _write_text, _write_json
from .core import convert, format_manager


#------------------------------------------------------------------------------
# Utility functions
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


# TODO: refactor these two functions
# TODO: allow the user to provide their own (de)serialization functions
def _read_file(file, from_):
    file_format = format_manager().file_type(from_)
    if file_format == 'text':
        return _read_text(file)
    elif file_format == 'json':
        return _read_json(file)
    else:
        raise ValueError("The file format '{0:s}' is ".format(file_format) +
                         "not supported (should be 'text' or 'json').")


def _write_file(file, to, contents):
    file_format = format_manager().file_type(to)
    if file_format == 'text':
        _write_text(file, contents)
    elif file_format == 'json':
        _write_json(file, contents)
    else:
        raise ValueError("The file format '{0:s}' is ".format(file_format) +
                         "not supported (should be 'text' or 'json').")


#------------------------------------------------------------------------------
# Conversion functions
#------------------------------------------------------------------------------

def _converted_filename(file, from_, to):
    base, from_extension = op.splitext(file)
    to_extension = format_manager().file_extension(to)
    return ''.join((base, to_extension))


def _cli(files_or_dirs, overwrite=None, from_=None, to=None):
    # Find all files.
    files = _expand_dirs_to_files(files_or_dirs)

    # Filter by from extension.
    from_extension = format_manager().file_extension(from_)
    files = _filter_files_by_extension(files, from_extension)

    # Convert all files.
    for file in files:
        print("Converting {0:s}...".format(file))
        contents = _read_file(file, from_)
        converted = convert(contents, from_, to)
        file_to = _converted_filename(file, from_, to)
        if op.exists(file_to) and not overwrite:
            print("The file already exists, please use --overwrite.")
            continue
        else:
            _write_file(file_to, to, converted)


def main():
    desc = 'Convert files across formats supported by ipymd.'
    parser = argparse.ArgumentParser(description=desc)

    parser.add_argument('files_or_dirs', nargs='+',
                        help=('list of files or directories to convert'))

    formats = ', '.join(format_manager().formats())
    parser.add_argument('--from', dest='from_', required=True,
                        help='one of {0:s}'.format(formats))

    parser.add_argument('--to', dest='to', required=True,
                        help='one of {0:s}'.format(formats))

    parser.add_argument('--overwrite', dest='overwrite', action='store_true',
                        help=('overwrite target file if it exists '
                              '(false by default)'))

    # Parse the CLI arguments.
    args = parser.parse_args()
    _cli(args.files_or_dirs,
         overwrite=args.overwrite,
         from_=args.from_,
         to=args.to,
         )


if __name__ == '__main__':
    main()

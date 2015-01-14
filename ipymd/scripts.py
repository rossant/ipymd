import argparse
import os
import os.path as op
import glob
import json
from ipymd.converters import nb_to_markdown, markdown_to_nb

def _flatten(l):
    return [item for sublist in l for item in sublist]

def _to_skip(dirname):
    return (op.basename(dirname).startswith('.') or
            op.basename(dirname).startswith('_'))

def _expand_dirs_to_files(files_or_dirs):
    files = []
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

def _read_md(file):
    with open(file, 'r') as f:
        return f.read()

def _write_md(file, contents):
    with open(file, 'w') as f:
        f.write(contents)

def _read_nb(file):
    with open(file, 'r') as f:
        return json.load(f)

def _write_nb(file, contents):
    with open(file, 'w') as f:
        return json.dump(contents, f, indent=2)

def main():
    parser = argparse.ArgumentParser(description=
                                     'Convert between ipynb and md.')

    parser.add_argument('files_or_dirs', nargs='+',
                        help=('list of ipynb or md files or directories '
                              'to convert'))

    parser.add_argument('--from', dest='convert_from', required=True,
                        help='either \'md\' or \'ipynb\'')

    parser.add_argument('--type', dest='type',
                        help='either markdown (default) or atlas')

    parser.add_argument('--overwrite', dest='overwrite', action='store_true',
                        help=('overwrite target file if it exists '
                              '(false by default)'))

    # Parse the CLI arguments.
    args = parser.parse_args()
    files_or_dirs = args.files_or_dirs
    md_type = args.type or 'markdown'
    overwrite = args.overwrite
    convert_from = args.convert_from

    # Find all files.
    files = _expand_dirs_to_files(files_or_dirs)

    # Filter as a function of --from.
    if convert_from == 'ipynb':
        files = _filter_files_by_extension(files, '.ipynb')
        convert = nb_to_markdown
        read = _read_nb
        write = _write_md
    elif convert_from in ('md', 'markdown'):
        files = _filter_files_by_extension(files, '.md')
        convert = markdown_to_nb
        read = _read_md
        write = _write_nb
    else:
        raise ValueError("'from' should be 'ipynb' or 'md'")

    for file in files:
        print("Converting {0:s}...".format(file))
        contents = read(file)
        converted = convert(contents)
        file_to = _converted_filename(file, convert_from)
        if op.exists(file_to) and not overwrite:
            print("The file already exists, please use --overwrite.")
            continue
        else:
            write(file_to, converted)

if __name__ == '__main__':
    main()

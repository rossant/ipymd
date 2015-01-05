import argparse
import os
import os.path as op
import glob
from ipymd.converters import nb_to_markdown, markdown_to_nb

def _flatten(l):
    return [item for sublist in l for item in sublist]

def _expand_dirs_to_files(files_or_dirs):
    files = []
    for file_or_dir in files_or_dirs:
        if op.isdir(file_or_dir):
            # Recursively visit the directories and add the files.
            files.extend(_expand_dirs_to_files(os.listdir(file_or_dir)))
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

def main():
    parser = argparse.ArgumentParser(description=
                                     'Convert between ipynb and md.')

    parser.add_argument('files_or_dirs', nargs='+',
                        help=('list of ipynb or md files or directories '
                              'to convert'))

    parser.add_argument('--from', dest='convert_from', required=True,
                        help='either md or ipynb')

    parser.add_argument('--type', dest='type',
                        help='either markdown (default) or atlas')

    parser.add_argument('--overwrite', dest='overwrite',
                        help=('overwrite target file if it exists '
                              '(false by default)'))

    args = parser.parse_args()
    files_or_dirs = args.files_or_dirs
    md_type = args.type or 'markdown'
    overwrite = args.overwrite
    convert_from = args.convert_from

    files = _expand_dirs_to_files(files_or_dirs)

    extensions = ['.ipymd' if convert_from == 'ipynb' else '.md']
    files_to_convert = _filter_files_by_extension(files, extensions)

if __name__ == '__main__':
    main()

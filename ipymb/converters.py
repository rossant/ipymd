import json
import re
from functools import partial

def get_metadata(filepath):
    with open(filepath, "r") as f:
        nb = json.load(f)

    cells = nb['worksheets'][0]['cells']

    cell = cells[0]
    assert cell.get('cell_type', None) == 'markdown'
    metadata = ''.join(cell.get('source', [])) + '\n\n'
    return metadata

def _indent_line(level=1, line=''):
    return ' ' * (4*level) + line

def process_cell_markdown(cell):
    return ''.join(cell.get('source', [])) + '\n\n'

def process_cell_heading(cell):
    return cell.get('level', 0) * '#' + ' ' + ''.join(cell.get('source', [])) + '\n\n'

def process_cell_input(cell):
    input_lines = cell.get('input', [])
    input_lines = map(partial(_indent_line, 0), input_lines)
    code = ''.join(input_lines)
    return code

def process_cell(cell):
    cell_type = cell.get('cell_type', None)

    if cell_type == 'markdown':
        return process_cell_markdown(cell)
    elif cell_type == 'heading':
        return process_cell_heading(cell)
    elif cell_type == 'code':
        return process_cell_input(cell)

def nb_to_markdown(filepath):
    with open(filepath, "r") as f:
        nb = json.load(f)

    cells = nb['worksheets'][0]['cells']
    md = '\n'.join([process_cell(_) for _ in cells])

    return md


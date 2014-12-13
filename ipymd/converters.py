import json
from functools import partial

def _indent_line(level=1, line=''):
    return ' ' * (4*level) + line

def process_cell_markdown(cell):
    return ''.join(cell.get('source', [])) + '\n'

def process_cell_heading(cell):
    return cell.get('level', 0) * '#' + ' ' + ''.join(cell.get('source', [])) + '\n'

def process_cell_input(cell, lang=None):
    # input_lines = cell.get('input', [])  # nbformat 3
    input_lines = cell.get('source', [])  # nbformat 4
    code = ''.join(input_lines)
    code = '```{0:s}\n'.format(lang or '') + code + '\n```\n'
    return code

def process_cell(cell, lang=None):
    cell_type = cell.get('cell_type', None)

    if cell_type == 'markdown':
        return process_cell_markdown(cell)
    elif cell_type == 'heading':
        return process_cell_heading(cell)
    elif cell_type == 'code':
        return process_cell_input(cell, lang=lang)

def _merge_successive_inputs(cells):
    """Return a new list of cells where successive input cells are merged
    together."""
    cells_merged = []
    is_last_input = False
    for cell in cells:
        cell_type = cell.get('cell_type', None)
        is_input = cell_type == 'code'
        # If the last cell and the current cell are input cells.
        if is_last_input and is_input:
            # Extend the last cell input with the new cell.
            cells_merged[-1]['source'].extend(['\n'] + cell['source'])
        else:
            cells_merged.append(cell)
        # Save the last input cell.
        is_last_input = is_input
    return cells_merged

def nb_to_markdown(filepath, saveto=None):
    with open(filepath, "r") as f:
        nb = json.load(f)
    # Only work for nbformat 4 for now.
    assert nb['nbformat'] >= 4
    # cells = n-b['worksheets'][0]['cells']  # nbformat 3
    cells = nb['cells']
    # Merge successive code inputs together.
    cells = _merge_successive_inputs(cells)
    # Find the notebook language.
    lang = nb['metadata']['language_info']['name']
    md = '\n'.join([process_cell(_, lang=lang) for _ in cells])
    if saveto is None:
        return md
    else:
        with open(saveto, "w") as f:
            f.write(md)

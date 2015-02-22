import json
import re
from functools import partial
from collections import OrderedDict

import IPython.nbformat as nbf

from .six import string_types, iteritems
from .htmlparser import get_html_contents

CODE_WRAP = {
    'markdown': '''```{lang}
{code}
```
''',

    'atlas': '''<pre data-code-language="{lang}"
     data-executable="true"
     data-type="programlisting">
{code}
</pre>
'''
}

MATH_WRAP = '''<span class="math-tex" data-type="tex">{equation}</span>'''

PROMPT_FIRST = '>>> '
PROMPT_NEXT = '... '

# nb to markdown
# -----------------------------------------------------------------------------
def _has_input_prompt(lines):
    """Return whether the line or set of lines has an input prompt."""
    if isinstance(lines, list):
        return any(line for line in lines if line.startswith(PROMPT_FIRST))
    else:
        return lines.startswith(PROMPT_FIRST) or lines.startswith(PROMPT_NEXT)

def _remove_prompt(line):
    if line.startswith(PROMPT_FIRST):
        return line[len(PROMPT_FIRST):]
    elif line.startswith(PROMPT_NEXT):
        return line[len(PROMPT_NEXT):]
    else:
        return line

def _add_prompt(source):
    """Add input prompts to code."""
    lines = source.strip().splitlines()
    lines_prompt = []
    prompt = PROMPT_FIRST
    lock = False
    for line in lines:
        if line.startswith('%%'):
            lines_prompt.append(prompt + line)
            prompt = PROMPT_NEXT
            lock = True
        elif line.startswith('#') or line.startswith('@'):
            lines_prompt.append(prompt + line)
            prompt = PROMPT_NEXT
        elif line.startswith('  '):
            prompt = PROMPT_NEXT
            lines_prompt.append(prompt + line)
            if not lock:
                prompt = PROMPT_FIRST
        else:
            lines_prompt.append(prompt + line)
            if not lock:
                prompt = PROMPT_FIRST
    return '\n'.join(lines_prompt)

def _get_code_input_output(lines):
    """Return the input and output lines with prompt for input lines."""
    if _has_input_prompt(lines):
        input = [_remove_prompt(line) for line in lines
                 if _has_input_prompt(line)]
        output = [line for line in lines
                  if not _has_input_prompt(line)]
        return '\n'.join(input), '\n'.join(output)
    else:
        return '\n'.join(lines), ''

def _ensure_string(source):
    # Ensure source is a string.
    if isinstance(source, list):
        input = '\n'.join([line.rstrip() for line in source])
    else:
        input = source
    return input

def _remove_math_span(source):
    # Remove any <span> equation tag that would be in a Markdown cell.
    source = source.replace('<span class="math-tex" data-type="tex">', '')
    source = source.replace('</span>', '')
    return source

def process_latex(text):
    regex = '''(?P<dollars>[\$]{1,2})([^\$]+)(?P=dollars)'''
    return re.sub(regex, MATH_WRAP.format(equation=r'\\\\(\2\\\\)'),
                  text)

def process_cell_markdown(cell, code_wrap=None):
    # Wrap math equations if code wrap is math.
    # source = cell.get('source', [])
    # text = ''.join(source) + '\n'
    text = _ensure_string(cell.get('source', [])) + '\n'
    if code_wrap == 'atlas':
        text = _remove_math_span(text)
        # Replace '$$eq$$' by '\\(eq\\)'.
        return process_latex(text)
    else:
        return text

def process_cell_input(cell, lang=None, code_wrap=None, add_prompt=None):
    # input_lines = cell.get('input', [])  # nbformat 3
    code = _ensure_string(cell.get('source', []))  # nbformat 4

    if add_prompt:
        outputs = cell.get('outputs', [])
        # Add stdout.
        output = ('\n'.join(_ensure_string(output.get('text', ''))
                            for output in outputs)).rstrip()
        # Add text output.
        output += ('\n'.join(_ensure_string(output.get('data', {}). \
                                                  get('text/plain', []))
                             for output in outputs)).rstrip()
        code = _add_prompt(code)
        if output.strip():
            code += '\n' + output.rstrip()

    return CODE_WRAP.get(code_wrap or
                         'markdown').format(lang=lang, code=code)

def process_cell(cell, lang=None, code_wrap=None, add_prompt=None):
    cell_type = cell.get('cell_type', None)
    if cell_type == 'markdown':
        return process_cell_markdown(cell, code_wrap=code_wrap)
    elif cell_type == 'code':
        return process_cell_input(cell, lang=lang,
                                  code_wrap=code_wrap,
                                  add_prompt=add_prompt)
    else:
        return cell.get('source', '')

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

def _load_nb_contents(contents_or_path):
    """Load a notebook contents from a dict or a path to a .ipynb file."""
    if isinstance(contents_or_path, string_types):
        with open(contents_or_path, "r") as f:
            return json.load(f)
    else:
        return contents_or_path

def nb_to_markdown(nb, code_wrap=None, add_prompt=None):
    """Convert a notebook contents to a Markdown document.

    Arguments:
    * nb : the notebook model
    * code_wrap: 'markdown' or 'atlas'

    """
    # Only work for nbformat 4 for now.
    assert nb['nbformat'] >= 4
    # cells = n-b['worksheets'][0]['cells']  # nbformat 3
    cells = nb['cells']
    # # Merge successive code inputs together.
    # cells = _merge_successive_inputs(cells)
    # Find the notebook language.
    lang = nb['metadata'].get('language_info', {}).get('name', 'python')
    md = '\n'.join([process_cell(_,
                   lang=lang,
                   code_wrap=code_wrap,
                   add_prompt=add_prompt)
                    for _ in cells])
    return md


# markdown to nb
# -----------------------------------------------------------------------------
class NotebookWriter(object):
    def __init__(self):
        self._nb = nbf.v4.new_notebook()

    def append_markdown(self, source):
        self._nb['cells'].append(nbf.v4.new_markdown_cell(source))

    def append_code(self, source):
        """If source does not contain a line starting with prompt, treat the
        whole source as Python code. Otherwise, the lines that do not start
        with prompt are treated as output."""
        lines = source.splitlines()
        if _has_input_prompt(lines):
            input, output = _get_code_input_output(lines)
            cell = nbf.v4.new_code_cell(input)
            if output:
                cell.outputs.append(nbf.v4.new_output('execute_result',
                                    {'text/plain': output},
                                    execution_count=None,
                                    metadata={},
                                    ))
            self._nb['cells'].append(cell)
        else:
            self._nb['cells'].append(nbf.v4.new_code_cell(source))

    @property
    def contents(self):
        return self._nb

    def save(self, filepath):
        with open(filepath, 'w') as f:
            nbf.write(self._nb, f)


# Part of the code below comes from mistune.
def preprocessing(text, tab=4):
    text = re.sub(r'\r\n|\r', '\n', text)
    text = text.replace('\t', ' ' * tab)
    text = text.replace('\u00a0', ' ')
    text = text.replace('\u2424', '\n')
    pattern = re.compile(r'^ +$', re.M)
    return pattern.sub('', text)


_tag = (
    r'(?!(?:'
    r'a|em|strong|small|s|cite|q|dfn|abbr|data|time|code|'
    r'var|samp|kbd|sub|sup|i|b|u|mark|ruby|rt|rp|bdi|bdo|'
    r'span|br|wbr|ins|del|img)\b)\w+(?!:/|[^\w\s@]*@)\b'
)


rules = OrderedDict([
    # Code block
    ('block_code', re.compile(r'^( {4}[^\n]+\n*)+')),
    ('fences', re.compile(
        r'^ *(`{3,}|~{3,}) *(\S+)? *\n'  # ```lang
        r'([\s\S]+?)\s*'
        r'\1 *(?:\n+|$)'  # ```
    )),
    # HTML block
    ('block_html', re.compile(
        r'^ *(?:%s|%s|%s) *(?:\n{2,}|\s*$)' % (
            r'<!--[\s\S]*?-->',
            r'<(%s)[\s\S]+?<\/\1>' % _tag,
            r'''<%s(?:"[^"]*"|'[^']*'|[^'">])*?>''' % _tag,
        )
    )),
    # Text until next new line.
    ('text', re.compile(r'^.+?\n\n|.+?$', re.DOTALL)),
    ('newline', re.compile(r'^\n+')),
    # ('text', re.compile(r'^.+')),
])


class MarkdownParser(object):
    def __init__(self):
        self._nb = NotebookWriter()

    def _manipulate(self, text):
        for key, rule in iteritems(rules):
            m = rule.match(text)
            if not m:
                continue
            getattr(self, 'parse_%s' % key)(m)
            return m
        return False

    def parse(self, text):
        text = preprocessing(text)
        text = text.strip()
        while text:
            m = self._manipulate(text)
            if m is not False:
                text = text[len(m.group(0)):]
                continue
            if text:
                raise RuntimeError('Infinite loop at: %s' % text)

    def parse_block_code(self, m):
        self._nb.append_code(m.group(0).strip())

    def parse_fences(self, m):
        lang = m.group(2)
        if lang == 'python':
            self._nb.append_code(m.group(3).strip())
        else:
            self._nb.append_markdown(m.group(0).strip())

    def parse_block_html(self, m):
        text = m.group(0).strip()

        if (text.startswith('<span class="math-tex"') and
            text.endswith('</span>')):
            # Replace '\\(' by '$$' in the notebook.
            text = text.replace(r'\\(', '$$')
            text = text.replace(r'\\)', '$$')

        self._nb.append_markdown(text.strip())

    def parse_text(self, m):
        text = m.group(0).strip()

        text = text.replace(r'\\(', '$')
        text = text.replace(r'\\)', '$')
        text = _remove_math_span(text)

        self._nb.append_markdown(text.strip())

    def parse_newline(self, m):
        pass

    @property
    def contents(self):
        return self._nb.contents


def markdown_to_nb(contents):
    parser = MarkdownParser()
    parser.parse(contents)
    return parser.contents

import json
from functools import partial
import IPython.nbformat as nbf
import mistune
from .six import string_types
from .htmlparser import get_html_contents

CODE_WRAP = {
    'markdown': '''
        ```{lang}
        {code}
        ```
        ''',

    'html': '''
        <pre data-code-language="{lang}" 
             data-executable="true" 
             data-type="programlisting">
        {code}
        </pre>
        '''
}

# nb to markdown
# -----------------------------------------------------------------------------
def process_cell_markdown(cell, code_wrap=None):
    # if code_wrap == 'math'
    # Wrap math equations if code wrap is math.
    source = cell.get('source', [])
    return ''.join(source) + '\n'

def process_cell_input(cell, lang=None, code_wrap=None):
    # input_lines = cell.get('input', [])  # nbformat 3
    input_lines = cell.get('source', [])  # nbformat 4
    code = ''.join(input_lines)
    # code = '```{0:s}\n'.format(lang or '') + code + '\n```\n'
    code = CODE_WRAP.get('code_wrap', 
                         'markdown').format(lang=lang, code=code)
    return code

def process_cell(cell, lang=None, code_wrap=None):
    cell_type = cell.get('cell_type', None)
    if cell_type == 'markdown':
        return process_cell_markdown(cell)
    elif cell_type == 'code':
        return process_cell_input(cell, lang=lang, code_wrap=code_wrap)

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

def nb_to_markdown(nb, code_wrap=None):
    """Convert a notebook contents to a Markdown document.

    Arguments:
    * nb : the notebook model
    * code_wrap: 'markdown' or 'html'

    """
    # Only work for nbformat 4 for now.
    assert nb['nbformat'] >= 4
    # cells = n-b['worksheets'][0]['cells']  # nbformat 3
    cells = nb['cells']
    # # Merge successive code inputs together.
    # cells = _merge_successive_inputs(cells)
    # Find the notebook language.
    lang = nb['metadata'].get('language_info', {}).get('name', 'python')
    md = '\n'.join([process_cell(_, lang=lang, code_wrap=code_wrap) for _ in cells])
    return md


# markdown to nb
# -----------------------------------------------------------------------------
class NotebookWriter(object):
    def __init__(self):
        self._nb = nbf.v4.new_notebook()

    def append_markdown(self, source):
        self._nb['cells'].append(nbf.v4.new_markdown_cell(source))

    def append_code(self, source):
        self._nb['cells'].append(nbf.v4.new_code_cell(source))

    @property
    def contents(self):
        return self._nb

    def save(self, filepath):
        with open(filepath, 'w') as f:
            nbf.write(self._nb, f)


class MyRenderer(object):
    def __init__(self, **kwargs):
        self.options = kwargs
        self.code_wrap = kwargs.get('code_wrap', 'markdown')
        self._nbwriter = NotebookWriter()

    def placeholder(self):
        return ''

    def block_code(self, code, lang):
        # Only explicit Python code becomes a code cell.
        if lang == 'python':
            self._nbwriter.append_code(code)
        else:
            self._nbwriter.append_markdown('```%s\n%s\n```' % (lang or '',
                                                               code.strip()))
        return code

    def block_quote(self, text):
        text = '\n'.join(('> ' + l)
                         for l in text.split('\n'))
        self._nbwriter.append_markdown(text)
        return text

    def block_html(self, html):
        type, contents = get_html_contents(html)
        # if self.code_wrap == 'html'
        # Strip special HTML tags for code and math
        if type == 'code':
            self._nbwriter.append_code(contents)
        elif type == 'math':
            self._nbwriter.append_markdown('$$%s$$' % contents)
        else:
            self._nbwriter.append_markdown(html)
        return html

    def header(self, text, level, raw=None):
        text = ('#' * level) + ' ' + text
        self._nbwriter.append_markdown(text)
        return text

    def hrule(self):
        return ''

    def list(self, body, ordered=True):
        items = body.strip().split('\n')
        if ordered:
            text = '\n'.join('%d. %s' % (i+1,s) for i,s in enumerate(items))
        else:
            text = '\n'.join('* %s' % _ for _ in items)
        self._nbwriter.append_markdown(text)
        return text

    def list_item(self, text):
        return text + '\n'

    def paragraph(self, text):
        self._nbwriter.append_markdown(text)
        return text

    def table(self, header, body):
        pass

    def table_row(self, content):
        pass

    def table_cell(self, content, **flags):
        pass

    def autolink(self, link, is_email=False):
        pass

    def codespan(self, text):
        return '`%s`' % text

    def double_emphasis(self, text):
        return '**%s**' % text

    def emphasis(self, text):
        return '*%s*' % text

    def image(self, src, title, alt_text):
        return '![%s](%s)' % (title or alt_text, src)

    def linebreak(self, ):
        return '\n'

    def newline(self, ):
        return '\n'

    def link(self, link, title, content):
        return '[%s](%s)' % (content or title, link)

    def tag(self, html):
        return html

    def strikethrough(self, text):
        return '~~%s~~' % text

    def text(self, text):
        return text


def markdown_to_nb(contents):
    """Convert a Markdown text to a notebook contents."""
    renderer = MyRenderer()
    md = mistune.Markdown(renderer=renderer)
    md.render(contents)
    return renderer._nbwriter.contents

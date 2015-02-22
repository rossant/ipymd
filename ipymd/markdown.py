# -*- coding: utf-8 -*-

"""Markdown readers and writers

Much of the code comes from the mistune library.

"""

#------------------------------------------------------------------------------
# Imports
#------------------------------------------------------------------------------

import re
from collections import OrderedDict

from .six import StringIO


#------------------------------------------------------------------------------
# Base Markdown reader
#------------------------------------------------------------------------------

def _preprocess(text, tab=4):
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


class BaseMarkdownReader(object):
    # TODO: named captured groups in the regexes
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

    def _manipulate(self, text):
        for key, rule in self.rules.items():
            m = rule.match(text)
            if not m:
                continue
            out = getattr(self, 'parse_%s' % key)(m)
            return m, out
        return False, {}

    def read(self, text):
        text = _preprocess(text)
        text = text.strip()
        while text:
            m, out = self._manipulate(text)
            yield out
            if m is not False:
                text = text[len(m.group(0)):]
                continue
            if text:
                raise RuntimeError('Infinite loop at: %s' % text)

    def parse_block_code(self, m):
        raise NotImplementedError("This method must be overriden.")

    def parse_fences(self, m):
        # 2: lang
        # 3: code
        raise NotImplementedError("This method must be overriden.")

    def parse_block_html(self, m):
        raise NotImplementedError("This method must be overriden.")

    def parse_text(self, m):
        raise NotImplementedError("This method must be overriden.")

    def parse_newline(self, m):
        pass

    def _code_cell(self, source):
        # Can be overriden to separate input/output from source.
        return {'cell_type': 'code',
                'input': source,
                'output': None}

    def _markdown_cell(self, source):
        return {'cell_type': 'markdown',
                'source': source}


#------------------------------------------------------------------------------
# Default Markdown reader
#------------------------------------------------------------------------------

# TODO: Configurable prompts
class MarkdownReader(BaseMarkdownReader):
    """Default Markdown reader."""

    prompt_first = '>>> '
    prompt_next = '... '

    # Handle code prompts
    # -------------------------------------------------------------------------

    def _has_input_prompt(self, lines):
        """Return whether the line or set of lines has an input prompt."""
        if isinstance(lines, list):
            return any(line for line in lines
                       if line.startswith(self.prompt_first))
        else:
            return (lines.startswith(self.prompt_first) or
                    lines.startswith(self.prompt_next))

    def _remove_prompt(self, line):
        """Remove the prompt in a line."""
        if line.startswith(self.prompt_first):
            return line[len(self.prompt_first):]
        elif line.startswith(self.prompt_next):
            return line[len(self.prompt_next):]
        else:
            return line

    def _get_code_input_output(self, lines):
        """Return the input and output lines with prompt for input lines."""
        if self._has_input_prompt(lines):
            input = [self._remove_prompt(line) for line in lines
                     if self._has_input_prompt(line)]
            output = [line for line in lines
                      if not self._has_input_prompt(line)]
            return '\n'.join(input), '\n'.join(output)
        else:
            return '\n'.join(lines), ''

    def _code_cell(self, source):
        """Split the source into input and output."""
        lines = source.splitlines()
        if self._has_input_prompt(lines):
            input, output = self._get_code_input_output(lines)
        else:
            input, output = source, None
        return {'cell_type': 'code',
                'input': input,
                'output': output}

    def _markdown_cell_from_regex(self, m):
        return self._markdown_cell(m.group(0).rstrip())

    # Parser methods
    # -------------------------------------------------------------------------

    def parse_fences(self, m):
        lang = m.group(2)
        if lang == 'python':
            return self._code_cell(m.group(3).rstrip())
        else:
            return self._markdown_cell_from_regex(m)

    def parse_block_code(self, m):
        return self._markdown_cell_from_regex(m)

    def parse_block_html(self, m):
        return self._markdown_cell_from_regex(m)

    def parse_text(self, m):
        return self._markdown_cell_from_regex(m)


#------------------------------------------------------------------------------
# Base Markdown writer
#------------------------------------------------------------------------------

class BaseMarkdownWriter(object):
    """Base Markdown writer."""

    def __init__(self):
        self._output = StringIO()

    def _new_paragraph(self):
        self._output.write('\n\n')

    def append_markdown(self, source):
        self._output.write(source.rstrip())

    def append_code(self, input, output=None):
        raise NotImplementedError("This method must be overriden.")

    @property
    def contents(self):
        return self._output.getvalue().rstrip()

    def save(self, filename):
        """Save the string into a text file."""
        with open(filename, 'w') as f:
            f.write(self.contents)

    def close(self):
        self._output.close()

    def __del__(self):
        self.close()


#------------------------------------------------------------------------------
# Default Markdown writer
#------------------------------------------------------------------------------

class MarkdownWriter(BaseMarkdownWriter):
    """Default Markdown writer."""

    prompt_first = MarkdownReader.prompt_first
    prompt_next = MarkdownReader.prompt_next

    def _add_prompt(self, source):
        """Add input prompts to code."""
        lines = source.strip().splitlines()
        lines_prompt = []
        prompt = self.prompt_first
        lock = False
        for line in lines:
            if line.startswith('%%'):
                lines_prompt.append(prompt + line)
                prompt = self.prompt_next
                lock = True
            elif line.startswith('#') or line.startswith('@'):
                lines_prompt.append(prompt + line)
                prompt = self.prompt_next
            elif line.startswith('  '):
                prompt = self.prompt_next
                lines_prompt.append(prompt + line)
                if not lock:
                    prompt = self.prompt_first
            else:
                lines_prompt.append(prompt + line)
                if not lock:
                    prompt = self.prompt_first
        return '\n'.join(lines_prompt).rstrip()

    def append_code(self, input, output=None):
        code = self._add_prompt(input)
        if output is not None:
            code += '\n' + output
        wrapped = '```python\n{code}\n```'.format(code=code.rstrip())
        self._output.write(wrapped)


def ipymd_cells_to_markdown(cells):
    """Convert a list of ipymd cells to a Markdown document."""
    writer = MarkdownWriter()
    for cell in cells:
        if cell['cell_type'] == 'markdown':
            writer.append_markdown(cell['source'])
            writer._new_paragraph()
        elif cell['cell_type'] == 'code':
            writer.append_code(cell['input'], cell['output'])
            writer._new_paragraph()
    return writer.contents

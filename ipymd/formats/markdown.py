# -*- coding: utf-8 -*-

"""Markdown readers and writers

Much of the code comes from the mistune library.

"""

#------------------------------------------------------------------------------
# Imports
#------------------------------------------------------------------------------

import re
from collections import OrderedDict

from ..ext.six import StringIO
from ..utils.utils import _ensure_string, _preprocess
from ..lib.markdown import (BlockGrammar, BlockLexer,
                            InlineGrammar, InlineLexer)


#------------------------------------------------------------------------------
# Base Markdown
#------------------------------------------------------------------------------

class BaseMarkdownReader(BlockLexer):
    def __init__(self):
        grammar = BlockGrammar()
        grammar.text = re.compile(r'^.+?\n\n|.+?$', re.DOTALL)
        rules = ['block_code', 'fences', 'block_html', 'text', 'newline']
        super(BaseMarkdownReader, self).__init__(grammar=grammar,
                                                 rules=rules,
                                                 yield_token=True)

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

    def _markdown_cell_from_regex(self, m):
        return self._markdown_cell(m.group(0).rstrip())


class BaseMarkdownWriter(object):
    """Base Markdown writer."""

    def __init__(self):
        self._output = StringIO()

    def _new_paragraph(self):
        self._output.write('\n\n')

    def append_markdown(self, source):
        source = _ensure_string(source)
        self._output.write(source.rstrip())

    def append_code(self, input, output=None):
        raise NotImplementedError("This method must be overriden.")

    def write(self, cell):
        if cell['cell_type'] == 'markdown':
            self.append_markdown(cell['source'])
        elif cell['cell_type'] == 'code':
            self.append_code(cell['input'], cell['output'])
        self._new_paragraph()

    @property
    def contents(self):
        return self._output.getvalue().rstrip() + '\n'  # end of file \n

    def close(self):
        self._output.close()

    def __del__(self):
        self.close()


#------------------------------------------------------------------------------
# Default Markdown
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
        # Note: the rstrip() is necessary for empty lines with the
        # leading '...' prompt but not the trailing space. See PR #25.
        if isinstance(lines, list):
            return any(line for line in lines
                       if line.startswith(self.prompt_first.rstrip()))
        else:
            return lines.startswith((self.prompt_first.rstrip(),
                                     self.prompt_next.rstrip()))

    def _remove_prompt(self, line):
        """Remove the prompt in a line."""
        if line.startswith(self.prompt_first.rstrip()):
            return line[len(self.prompt_first):]
        elif line.startswith(self.prompt_next.rstrip()):
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

    # Helper functions to generate ipymd cells
    # -------------------------------------------------------------------------

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
            # Empty line = second prompt.
            elif line.rstrip() == '':
                lines_prompt.append((self.prompt_next + line).rstrip())
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


MARKDOWN_FORMAT = dict(
    name='markdown',
    reader=MarkdownReader,
    writer=MarkdownWriter,
    file_extension='.md',
    file_type='text',
)

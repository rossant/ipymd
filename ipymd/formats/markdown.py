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
from ..core.prompt import create_prompt


#------------------------------------------------------------------------------
# Base Markdown
#------------------------------------------------------------------------------

class BaseMarkdownReader(BlockLexer):
    def __init__(self):
        grammar = BlockGrammar()
        grammar.text = re.compile(r'^.+?\n\n|.+?$', re.DOTALL)
        rules = ['block_code', 'fences', 'block_html', 'text', 'newline']
        super(BaseMarkdownReader, self).__init__(grammar=grammar,
                                                 rules=rules)

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

class MarkdownReader(BaseMarkdownReader):
    """Default Markdown reader."""

    def __init__(self, prompt=None):
        super(MarkdownReader, self).__init__()
        self._prompt = create_prompt(prompt)

    # Helper functions to generate ipymd cells
    # -------------------------------------------------------------------------

    def _code_cell(self, source):
        """Split the source into input and output."""
        input, output = self._prompt.to_cell(source)
        return {'cell_type': 'code',
                'input': input,
                'output': output}

    # Parser methods
    # -------------------------------------------------------------------------

    def parse_fences(self, m):
        lang = m.group(2)
        code = m.group(3).rstrip()
        if lang == 'python':
            return self._code_cell(code)
        else:
            # Test the first line of the cell.
            first_line = code.splitlines()[0]
            if self._prompt.is_input(first_line):
                return self._code_cell(code)
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

    def __init__(self, prompt=None):
        super(MarkdownWriter, self).__init__()
        self._prompt = create_prompt(prompt)

    def append_code(self, input, output=None):
        code = self._prompt.from_cell(input, output)
        wrapped = '```python\n{code}\n```'.format(code=code.rstrip())
        self._output.write(wrapped)


MARKDOWN_FORMAT = dict(
    name='markdown',
    reader=MarkdownReader,
    writer=MarkdownWriter,
    file_extension='.md',
    file_type='text',
)

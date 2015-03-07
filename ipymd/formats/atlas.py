# -*- coding: utf-8 -*-

"""Atlas readers and writers."""

#------------------------------------------------------------------------------
# Imports
#------------------------------------------------------------------------------

import re

from .markdown import BaseMarkdownReader, BaseMarkdownWriter
from ..ext.six.moves.html_parser import HTMLParser
from ..ext.six.moves.html_entities import name2codepoint
from ..utils.utils import _ensure_string


#------------------------------------------------------------------------------
# HTML utility functions
#------------------------------------------------------------------------------

class MyHTMLParser(HTMLParser):
    def __init__(self, *args, **kwargs):
        HTMLParser.__init__(self, *args, **kwargs)
        self.is_code = False
        self.is_math = False
        self.display = ''
        self.data = ''

    def handle_starttag(self, tag, attrs):
        if tag == 'pre' and ('data-type', 'programlisting') in attrs:
            self.is_code = True
        elif tag == 'span' and ('data-type', 'tex') in attrs:
            self.is_math = True

        if ('data-display', 'inline') in attrs:
            self.display = 'inline'
        elif ('data-display', 'block') in attrs:
            self.display = 'block'

    def handle_data(self, data):
        if self.is_code:
            self.data += data
        elif self.is_math:
            self.data += data


def _get_html_contents(html):
    """Process a HTML block and detects whether it is a code block,
    a math block, or a regular HTML block."""
    parser = MyHTMLParser()
    parser.feed(html)
    if parser.is_code:
        return ('code', parser.data.strip())
    elif parser.is_math:
        return ('math', parser.data.strip())
    else:
        return '', ''


#------------------------------------------------------------------------------
# Atlas
#------------------------------------------------------------------------------

class AtlasReader(BaseMarkdownReader):

    code_wrap = ('<pre data-code-language="{lang}"\n'
                 '     data-executable="true"\n'
                 '     data-type="programlisting">\n'
                 '{code}\n'
                 '</pre>')

    math_wrap = '<span class="math-tex" data-type="tex">{equation}</span>'

    # Utility methods
    # -------------------------------------------------------------------------

    def _remove_math_span(self, source):
        # Remove any <span> equation tag that would be in a Markdown cell.
        source = source.replace('<span class="math-tex" data-type="tex">', '')
        source = source.replace('</span>', '')
        return source

    # Parser
    # -------------------------------------------------------------------------

    def parse_fences(self, m):
        return self._markdown_cell_from_regex(m)

    def parse_block_code(self, m):
        return self._markdown_cell_from_regex(m)

    def parse_block_html(self, m):
        text = m.group(0).strip()

        type, contents = _get_html_contents(text)
        if type == 'code':
            return self._code_cell(contents)
        elif type == 'math':
            return self._markdown_cell(contents)
        else:
            return self._markdown_cell(text)

    def parse_text(self, m):
        text = m.group(0).strip()

        if (text.startswith('<span class="math-tex"') and
           text.endswith('</span>')):
            # Replace '\\(' by '$$' in the notebook.
            text = text.replace('\\\\(', '$$')
            text = text.replace('\\\\)', '$$')
            text = text.strip()
        else:
            # Process math equations.
            text = text.replace('\\\\(', '$')
            text = text.replace('\\\\)', '$')

        # Remove the math <span>.
        text = self._remove_math_span(text)

        # Add the processed Markdown cell.
        return self._markdown_cell(text.strip())


class AtlasWriter(BaseMarkdownWriter):

    _math_regex = '''(?P<dollars>[\$]{1,2})([^\$]+)(?P=dollars)'''

    def append_markdown(self, source):
        source = _ensure_string(source)
        # Wrap math equations.
        source = re.sub(self._math_regex,
                        AtlasReader.math_wrap.format(equation=r'\\\\(\2\\\\)'),
                        source)
        # Write the processed Markdown.
        self._output.write(source.rstrip())

    def append_code(self, input, output=None):
        # Wrap code.
        wrapped = AtlasReader.code_wrap.format(lang='python', code=input)
        # Write the HTML code block.
        self._output.write(wrapped)


ATLAS_FORMAT = dict(
    name='atlas',
    reader=AtlasReader,
    writer=AtlasWriter,
    file_extension='.md',
    file_type='text',
)

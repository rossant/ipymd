# -*- coding: utf-8 -*-

"""Markdown readers and writers

Much of the code comes from the mistune library.

"""

#------------------------------------------------------------------------------
# Imports
#------------------------------------------------------------------------------

import re
from collections import OrderedDict


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
        raise NotImplementedError("This method must be overriden.")


#------------------------------------------------------------------------------
# Default Markdown reader
#------------------------------------------------------------------------------

class MarkdownReader(BaseMarkdownReader):
    def parse_block_code(self, m):
        pass

    def parse_fences(self, m):
        pass

    def parse_block_html(self, m):
        pass

    def parse_text(self, m):
        pass

    def parse_newline(self, m):
        pass

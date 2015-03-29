# -*- coding: utf-8 -*-

"""OpenDocument routines."""


# -----------------------------------------------------------------------------
# Imports
# -----------------------------------------------------------------------------

import os
import os.path as op
import re
from contextlib import contextmanager
from pprint import pprint

try:
    import odf
except ImportError:
    raise ImportError("The odfpy library is required.")
from odf.opendocument import OpenDocument, OpenDocumentText, load
from odf.style import (Style,
                       TextProperties,
                       ParagraphProperties,
                       ListLevelProperties,
                       ListLevelLabelAlignment)
from odf.text import (H, P, S, Span, LineBreak, List, ListItem,
                      ListStyle, ListLevelStyleNumber)

from ..ext.six import text_type, string_types
from .base_lexer import BaseRenderer
from .markdown import BaseRenderer, InlineLexer, MarkdownWriter, BlockLexer


# -----------------------------------------------------------------------------
# Utility functions
# -----------------------------------------------------------------------------

_STYLE_NAMES = (('urn:oasis:names:tc:opendocument:xmlns:style:1.0',
                'display-name'),
                ('urn:oasis:names:tc:opendocument:xmlns:style:1.0',
                'name'))


def _show_attrs(el):
    if not el.attributes:
        return ''
    return ', '.join('"{0}"="{1}"'.format(k, v)
                     for k, v in el.attributes.items())


def _tag_data(el):
    if hasattr(el, 'data'):
        return el.data
    else:
        return ''


def _tag_name(el):
    return (el.tagName.replace('text:', '').lower().strip())


def _show_element(el, indent=''):
    if hasattr(el, 'tagName'):
        print(indent + el.tagName + ' - ' +
              _show_attrs(el) + ' | ' + _tag_data(el))
    for child in el.childNodes:
        _show_element(child, indent + '  ')


def _is_paragraph(el):
    return el.tagName == 'text:p'


def _is_normal_text(item):
    return (item['tag'] == 'span' and
            item.get('style', 'normal-text') == 'normal-text')


def _merge_text(*children):
    children = list(children)
    if not children:
        return children
    head, tail = children[0:1], children[1:]
    if _is_normal_text(head[0]):
        if not tail:
            return head
        else:
            merged = _merge_text(*tail)
            if _is_normal_text(merged[0]):
                merged[0]['text'] = head[0]['text'] + merged[0]['text']
                return merged
            else:
                return head + merged
    else:
        return head + _merge_text(*tail)


def _is_empty(el):
    if _is_paragraph(el):
        return not(el.childNodes)
    return False


def load_odf(path):
    # HACK: work around a bug in odfpy: make sure the path string is unicode.
    path = text_type(path)
    doc = load(path)
    return ODFDocument(doc=doc)


def save_odf(path, contents):
    contents.save(path)


# -----------------------------------------------------------------------------
# Style-related utility functions
# -----------------------------------------------------------------------------

def _numbered_style():
    """Create a numbered list style."""

    style = ListStyle(name='_numbered_list')

    lls = ListLevelStyleNumber(level=1)

    lls.setAttribute('displaylevels', 1)
    lls.setAttribute('numsuffix', '. ')
    lls.setAttribute('numformat', '1')

    llp = ListLevelProperties()
    llp.setAttribute('listlevelpositionandspacemode', 'label-alignment')

    llla = ListLevelLabelAlignment(labelfollowedby='listtab')
    llla.setAttribute('listtabstopposition', '1.27cm')
    llla.setAttribute('textindent', '-0.635cm')
    llla.setAttribute('marginleft', '1.27cm')

    llp.addElement(llla)

    # llp.setAttribute('spacebefore', '')
    # llp.setAttribute('minlabelwidth', '')
    lls.addElement(llp)

    style.addElement(lls)

    return style


def _create_style(name, family=None, **kwargs):
    """Helper function for creating a new style."""
    if family == 'paragraph' and 'marginbottom' not in kwargs:
        kwargs['marginbottom'] = '.5cm'
    style = Style(name=name, family=family)
    # Extract paragraph properties.
    kwargs_par = {}
    keys = sorted(kwargs.keys())
    for k in keys:
        if 'margin' in k:
            kwargs_par[k] = kwargs.pop(k)
    style.addElement(TextProperties(**kwargs))
    if kwargs_par:
        style.addElement(ParagraphProperties(**kwargs_par))
    return style


def default_styles():
    """Generate default ODF styles."""

    styles = {}

    def _add_style(name, **kwargs):
        styles[name] = _create_style(name, **kwargs)

    _add_style('heading-1',
               family='paragraph',
               fontsize='24pt',
               fontweight='bold',
               )
    _add_style('heading-2',
               family='paragraph',
               fontsize='22pt',
               fontweight='bold',
               )
    _add_style('heading-3',
               family='paragraph',
               fontsize='20pt',
               fontweight='bold',
               )
    _add_style('heading-4',
               family='paragraph',
               fontsize='18pt',
               fontweight='bold',
               )
    _add_style('heading-5',
               family='paragraph',
               fontsize='16pt',
               fontweight='bold',
               )
    _add_style('heading-6',
               family='paragraph',
               fontsize='14pt',
               fontweight='bold',
               )
    _add_style('normal-paragraph',
               family='paragraph',
               fontsize='12pt',
               marginbottom='0.25cm',
               )
    _add_style('code',
               family='paragraph',
               fontsize='10pt',
               fontweight='bold',
               fontfamily='Courier New',
               color='#555555',
               )
    _add_style('quote',
               family='paragraph',
               fontsize='12pt',
               fontstyle='italic',
               )
    _add_style('list-paragraph',
               family='paragraph',
               fontsize='12pt',
               marginbottom='.1cm',
               )
    _add_style('sublist-paragraph',
               family='paragraph',
               fontsize='12pt',
               marginbottom='.1cm',
               )
    _add_style('numbered-list-paragraph',
               family='paragraph',
               fontsize='12pt',
               marginbottom='.1cm',
               )

    _add_style('normal-text',
               family='text',
               fontsize='12pt',
               )
    _add_style('italic',
               family='text',
               fontstyle='italic',
               fontsize='12pt',
               )
    _add_style('bold',
               family='text',
               fontweight='bold',
               fontsize='12pt',
               )
    _add_style('url',
               family='text',
               fontsize='12pt',
               fontweight='bold',
               fontfamily='Courier',
               )
    _add_style('inline-code',
               family='text',
               fontsize='10pt',
               fontweight='bold',
               fontfamily='Courier New',
               color='#555555',
               )

    styles['_numbered_list'] = _numbered_style()

    return styles


def _style_name(el):
    for name in _STYLE_NAMES:
        out = el.attributes.get(name, '').strip()
        if out:
            return out
    return ''


def load_styles(path_or_doc):
    """Return a dictionary of all styles contained in an ODF document."""
    if isinstance(path_or_doc, string_types):
        doc = load(path_or_doc)
    else:
        # Recover the OpenDocumentText instance.
        if isinstance(path_or_doc, ODFDocument):
            doc = path_or_doc._doc
        else:
            doc = path_or_doc
        assert isinstance(doc, OpenDocument), doc
    styles = {_style_name(style): style for style in doc.styles.childNodes}
    return styles


class StyleManager(object):
    def __init__(self, styles=None, mapping=None):
        self._default = default_styles()
        self._styles = styles or self._default

        # Mapping and inverse mapping.
        self._mapping = mapping
        if mapping:
            assert set(mapping.keys()) <= set(self._default.keys())
            self._inverse_mapping = {v: k for (k, v) in mapping.items()}

    @property
    def styles(self):
        return self._styles

    def __getitem__(self, name):
        if name is None:
            return None
        if not self._mapping:
            return name
        if name in self._default:
            actual_name = self._mapping.get(name, name)
            return actual_name
        elif name in self._styles:
            return name
        else:
            raise ValueError("The style '{0}' hasn't been ".format(name) +
                             "defined.")


# -----------------------------------------------------------------------------
# ODF Document
# -----------------------------------------------------------------------------

class ODFDocument(object):
    def __init__(self, styles=None, style_mapping=None, doc=None):

        # Create the document.
        self._doc = doc or OpenDocumentText()

        # Load styles.
        if styles is None and doc is not None:
            styles = load_styles(doc)

        # Create the style manager.
        self._style_manager = StyleManager(styles=styles,
                                           mapping=style_mapping)
        self.add_styles(**self._style_manager.styles)

        self._containers = []  # Stack of currently-active containers.
        self._next_p_style = None  # Style of the next paragraph to be created.
        self._ordered = False  # Where we're currently in an ordered list.

    # Public methods
    # -------------------------------------------------------------------------

    def show(self):
        _show_element(self._doc.text)

    def save(self, path):
        self._doc.save(path)

    # Style methods
    # -------------------------------------------------------------------------

    def add_styles(self, **styles):
        """Add ODF styles to the current document."""
        for stylename in sorted(styles):
            self._doc.styles.addElement(styles[stylename])

    def _get_style_name(self, name):
        """Return a style from its default or actual name."""
        return self._style_manager[name]

    @property
    def styles(self):
        return self._style_manager.styles

    def show_styles(self):
        pprint(self.styles)

    def tree(self, el=None):
        item = {}
        # Name.
        if el is None:
            el = self._doc.text
            item['tag'] = 'root'
        else:
            item['tag'] = _tag_name(el)
        # Data.
        item['data'] = _tag_data(el)
        if item['tag'] == 's':
            item['count'] = int(el.attributes.get(
                ('urn:oasis:names:tc:opendocument:xmlns:text:1.0', 'c'), 1))
        # Children.
        children = [self.tree(child) for child in el.childNodes
                    if not _is_empty(child)]
        if (len(children) == 1) and (children[0]['tag'] == 'text'):
            item['text'] = children[0]['data']
        else:
            item['children'] = children
        # Style.
        item['style'] = self._style_name(el)
        # Merge consecutive text children.
        if item.get('children', []):
            item['children'] = _merge_text(*item['children'])
        # Remove empty fields.
        item = {k: v for k, v in item.items() if v}
        return item

    def __eq__(self, other):
        return self.tree() == other.tree()

    # Internal methods
    # -------------------------------------------------------------------------

    @property
    def _item_level(self):
        """Return the current item level."""
        return len([c for c in self._containers
                   if 'list-item' in c.tagName])

    def _replace_stylename(self, kwargs):
        if 'stylename' in kwargs:
            if isinstance(kwargs['stylename'], string_types):
                kwargs['stylename'] = self._get_style_name(kwargs['stylename'])
        return kwargs

    def _add_element(self, cls, **kwargs):
        """Add an element."""
        # Convert stylename strings to actual style elements.
        kwargs = self._replace_stylename(kwargs)
        el = cls(**kwargs)
        self._doc.text.addElement(el)

    def _style_name(self, el):
        """Return the style name of an element."""
        if el.attributes is None:
            return None
        style_field = ('urn:oasis:names:tc:opendocument:xmlns:text:1.0',
                       'style-name')
        name = el.attributes.get(style_field, None)
        if not name:
            return None
        return self._get_style_name(name)

    # Block methods
    # -------------------------------------------------------------------------

    def heading(self, text, level):
        if level not in range(1, 7):
            raise ValueError("Heading 'level' should be between 1 and 6.")
        stylename = ('heading-{0:d}'.format(level))
        self._add_element(H, outlinelevel=level, text=text,
                          stylename=stylename)

    def start_container(self, cls, **kwargs):
        """Append a new container."""
        # Convert stylename strings to actual style elements.
        kwargs = self._replace_stylename(kwargs)
        # Create the container.
        container = cls(**kwargs)
        self._containers.append(container)

    def end_container(self, cancel=None):
        """Finishes and registers the currently-active container, unless
        'cancel' is True."""
        if not self._containers:
            return
        container = self._containers.pop()
        if len(self._containers) >= 1:
            parent = self._containers[-1]
        else:
            parent = self._doc.text
        if not cancel:
            parent.addElement(container)

    @contextmanager
    def container(self, cls, **kwargs):
        """Container context manager."""
        self.start_container(cls, **kwargs)
        yield
        self.end_container()

    def start_paragraph(self, stylename=None):
        """Start a new paragraph."""
        # Use the next paragraph style if one was set.
        if stylename is None:
            stylename = self._next_p_style or 'normal-paragraph'
        self.start_container(P, stylename=stylename)

    def is_in_paragraph(self):
        return self._containers and _is_paragraph(self._containers[-1])

    def end_paragraph(self, cancel=None):
        """End the current paragraph."""
        self.end_container(cancel=cancel)

    def require_paragraph(self):
        """Create a new paragraph unless the currently-active container
        is already a paragraph."""
        if self._containers and _is_paragraph(self._containers[-1]):
            return False
        else:
            self.start_paragraph()
            return True

    @contextmanager
    def paragraph(self, stylename=None):
        """Paragraph context manager."""
        self.start_paragraph(stylename=stylename)
        yield
        self.end_paragraph()

    def _code_line(self, line):
        """Add a code line."""
        assert self._containers
        container = self._containers[-1]
        # Handle extra spaces.
        text = line
        while text:
            if text.startswith('  '):
                r = re.match(r'(^ +)', text)
                n = len(r.group(1))
                container.addElement(S(c=n))
                text = text[n:]
            elif '  ' in text:
                assert not text.startswith(' ')
                i = text.index('  ')
                container.addElement(Span(text=text[:i]))
                text = text[i:]
            else:
                container.addElement(Span(text=text))
                text = ''

    def code(self, text, lang=None):
        """Add a code block."""
        # WARNING: lang is discarded currently.
        with self.paragraph(stylename='code'):
            lines = text.splitlines()
            for line in lines[:-1]:
                self._code_line(line)
                self.linebreak()
            self._code_line(lines[-1])

    def set_next_paragraph_style(self, style):
        self._next_p_style = style

    def next_paragraph_style(self):
        return self._next_p_style

    def clear_next_paragraph_style(self):
        self._next_p_style = None

    def start_quote(self):
        """Start a block quote. Require a new paragraph afterwards."""
        self.set_next_paragraph_style('quote')

    def end_quote(self):
        """End a block quote."""
        self.clear_next_paragraph_style()

    # List methods
    # -------------------------------------------------------------------------

    def start_numbered_list(self):
        """Start a numbered list."""
        self._ordered = True
        self.start_container(List, stylename='_numbered_list')
        self.set_next_paragraph_style('numbered-list-paragraph'
                                      if self._item_level <= 0
                                      else 'sublist-paragraph')

    def end_numbered_list(self):
        """End a numbered list."""
        self.clear_next_paragraph_style()
        self.end_container()
        self._ordered = None

    def start_list(self):
        """Start a list."""
        self._ordered = False
        self.start_container(List)
        self.set_next_paragraph_style('list-paragraph'
                                      if self._item_level <= 0
                                      else 'sublist-paragraph')

    def end_list(self):
        """End a list."""
        self.end_container()
        self.clear_next_paragraph_style()

    @contextmanager
    def list(self):
        """List context manager."""
        self.start_list()
        yield
        self.end_list()

    @contextmanager
    def numbered_list(self):
        """Numbered list context manager."""
        self.start_numbered_list()
        yield
        self.end_numbered_list()

    def start_list_item(self):
        """Start a list item."""
        self.start_container(ListItem)

    def end_list_item(self):
        """End a list item."""
        self.end_container()

    @contextmanager
    def list_item(self):
        """List item context manager."""
        self.start_list_item()
        yield
        self.end_list_item()

    # Inline methods
    # -------------------------------------------------------------------------

    def text(self, text, stylename=None):
        """Add text within the current container."""
        assert self._containers
        container = self._containers[-1]
        if stylename is not None:
            stylename = self._get_style_name(stylename)
            container.addElement(Span(stylename=stylename, text=text))
        else:
            container.addElement(Span(text=text))

    def link(self, url):
        self.text(url, stylename='url')

    def bold(self, text):
        self.text(text, stylename='bold')

    def inline_code(self, text):
        self.text(text, stylename='inline-code')

    def italic(self, text):
        self.text(text, stylename='italic')

    def linebreak(self):
        """Add a line break within a paragraph."""
        container = self._containers[-1]
        container.addElement(LineBreak())


# -----------------------------------------------------------------------------
# Renderers
# -----------------------------------------------------------------------------

class ODFInlineRenderer(BaseRenderer):
    def __init__(self, doc):
        super(ODFInlineRenderer, self).__init__()
        self._doc = doc

    def text(self, text):
        self._doc.text(text)

    def autolink(self, link, is_email=False):
        self._doc.link(link)

    def codespan(self, text):
        self._doc.inline_code(text)

    def double_emphasis(self, text):
        self._doc.bold(text)

    def emphasis(self, text):
        self._doc.italic(text)

    def image(self, src, title, alt_text):
        # TODO
        pass

    def linebreak(self):
        self._doc.linebreak()

    def link(self, link, title, content):
        self._doc.text(content + ' (')
        self._doc.link(link)
        self._doc.text(')')


class ODFRenderer(BaseRenderer):
    def __init__(self, doc):
        super(ODFRenderer, self).__init__()
        self._doc = doc
        self._paragraph_created_after_item_start = None

    def text(self, text):
        inline_renderer = ODFInlineRenderer(self._doc)
        inline_lexer = InlineLexer(renderer=inline_renderer)
        inline_lexer.read(text)

    def paragraph(self, text):
        with self._doc.paragraph():
            self.text(text)

    def block_html(self, text, pre=None):
        self.paragraph(text)

    def block_quote_start(self):
        self._doc.start_quote()

    def block_quote_end(self):
        self._doc.end_quote()

    def heading(self, text, level=None):
        self._doc.heading(text, level)

    def list_start(self, ordered=False):
        if self._doc.is_in_paragraph():
            self._doc.end_paragraph()
        if ordered:
            self._doc.start_numbered_list()
        else:
            self._doc.start_list()

    def list_end(self):
        self._doc.end_list()

    def list_item_start(self):
        self._doc.start_list_item()
        self._doc.start_paragraph()

    def loose_item_start(self):
        self.list_item_start()

    def list_item_end(self):
        if self._doc.is_in_paragraph():
            self._doc.end_paragraph()
        self._doc.end_list_item()

    def block_code(self, code, lang=None):
        self._doc.code(code, lang=lang)


# -----------------------------------------------------------------------------
# ODF reader
# -----------------------------------------------------------------------------

def _item_type(item):
    """Indicate to the ODF reader the type of the block or text."""
    tag = item['tag']
    style = item.get('style', None)
    if tag == 'p':
        if style is None or 'paragraph' in style:
            return 'paragraph'
        else:
            return style
    elif tag == 'span':
        if style in (None, 'normal-text'):
            return 'text'
        elif style == 'url':
            return 'link'
        else:
            return style
    elif tag == 'h':
        assert style is not None
        return style
    elif tag in ('list', 'list-item', 'line-break'):
        if style == '_numbered_list':
            return 'numbered-list'
        else:
            return tag
    elif tag == 's':
        return 'spaces'
    raise Exception("The tag '{0}' with style '{1}' hasn't "
                    "been implemented.".format(tag, style))


class BaseODFReader(BaseRenderer):
    """Parse an ODF document."""
    def read(self, doc):
        # tag, style, children, text
        assert isinstance(doc, ODFDocument)
        self._doc = doc
        self._dict = doc.tree()
        assert self._dict['tag'] == 'root'
        for child in self._dict['children']:
            self._read_item(child)

    def _process_children(self, item):
        # Process the children recursively.
        children = item.get('children', [])
        for child in children:
            self._read_item(child)

    def _read_item(self, item):
        # Process the current item.
        text = item.get('text', None)
        item_type = _item_type(item)

        # Block items.
        if item_type.startswith('heading'):
            self.heading(text, level=int(item_type[-1]))
        elif item_type == 'paragraph':
            self.paragraph_start()
            self._process_children(item)
            self.paragraph_end()
        elif item_type == 'quote':
            self.quote_start()
            self._process_children(item)
            self.quote_end()
        elif item_type == 'code':
            self.code_start(lang=item.get('lang', None))
            self._process_children(item)
            self.code_end()
        elif item_type == 'list':
            self.list_start()
            self._process_children(item)
            self.list_end()
        elif item_type == 'numbered-list':
            self.numbered_list_start()
            self._process_children(item)
            self.numbered_list_end()
        elif item_type == 'list-item':
            self.list_item_start()
            self._process_children(item)
            self.list_item_end()

        # Inline items.
        elif item_type == 'line-break':
            self.linebreak()
        elif item_type == 'text':
            self.text(text)
        elif item_type == 'inline-code':
            self.codespan(text)
        elif item_type == 'bold':
            self.bold(text)
        elif item_type == 'italic':
            self.italic(text)
        elif item_type == 'link':
            self.link(text)
        elif item_type == 'spaces':
            self.spaces(item.get('count', 1))
        # elif item_type == 'image':
        else:
            raise NotImplementedError(item_type, item)


# -----------------------------------------------------------------------------
# ODF => Markdown converter
# -----------------------------------------------------------------------------

class ODFMarkdownConverter(BaseODFReader):
    def __init__(self):
        self._writer = MarkdownWriter()
        self._in_list = None  # None, 'list' or 'numbered'
        self._list_level = 0

    @property
    def contents(self):
        return self._writer.contents

    # -------------------------------------------------------------------------
    # Block
    # -------------------------------------------------------------------------

    def heading(self, text, level):
        self._writer.heading(text, level=level)
        self._writer.newline()

    def newline(self):
        self._writer.newline()

    def paragraph_start(self):
        # self._writer.newline()
        pass

    def paragraph_end(self):
        if self._in_list:
            self._writer.linebreak()
        else:
            self._writer.newline()

    def quote_start(self):
        # self._writer.newline()
        self._writer.quote_start()

    def quote_end(self):
        self._writer.quote_end()
        self._writer.newline()

    def code_start(self, lang=None):
        self._writer.code_start(lang=lang)

    def code_end(self):
        self._writer.code_end()
        self._writer.newline()

    # -------------------------------------------------------------------------
    # Lists
    # -------------------------------------------------------------------------

    def list_start(self, kind='list'):
        self._list_level += 1
        self._in_list = kind

    def list_end(self):
        # self._writer.newline()
        self._list_level -= 1
        if self._list_level == 0:
            self._in_list = None
            self._writer.linebreak()

    def numbered_list_start(self):
        self.list_start('numbered')

    def numbered_list_end(self):
        self.list_end()

    def list_item_start(self):
        if self._in_list == 'list':
            self._writer.list_item(level=(self._list_level - 1))
        if self._in_list == 'numbered':
            self._writer.numbered_list_item(level=(self._list_level - 1))

    def list_item_end(self):
        # self._writer.linebreak()
        pass

    # -------------------------------------------------------------------------
    # Inline
    # -------------------------------------------------------------------------

    def spaces(self, count=1):
        self._writer.text(' ' * count)

    def codespan(self, text):
        self._writer.inline_code(text)

    def bold(self, text):
        self._writer.bold(text)

    def italic(self, text):
        self._writer.italic(text)

    def linebreak(self):
        self._writer.linebreak()

    def image(self, caption, url):
        self._writer.image(caption, url)

    def link(self, url):
        self._writer.text(url)

    def text(self, text):
        self._writer.text(text)


def odf_to_markdown(doc):
    converter = ODFMarkdownConverter()
    converter.read(doc)
    return converter.contents


def markdown_to_odf(md):
    doc = ODFDocument()
    renderer = ODFRenderer(doc)
    block_lexer = BlockLexer(renderer=renderer)
    block_lexer.read(md)
    return doc

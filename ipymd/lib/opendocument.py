# -*- coding: utf-8 -*-

"""OpenDocument routines."""


# -----------------------------------------------------------------------------
# Imports
# -----------------------------------------------------------------------------

import os
import os.path as op
from contextlib import contextmanager
from pprint import pprint

try:
    import odf
except ImportError:
    raise ValueError("The odfpy library is required.")
from odf.opendocument import OpenDocumentText, load
from odf.style import (Style, TextProperties, ListLevelProperties,
                       ListLevelLabelAlignment)
from odf.text import (H, P, Span, LineBreak, List, ListItem,
                      ListStyle, ListLevelStyleNumber)

from ..ext.six import string_types


# -----------------------------------------------------------------------------
# Utility functions
# -----------------------------------------------------------------------------

def _show_attrs(el):
    if not el.attributes:
        return ''
    return ', '.join('"{0}"="{1}"'.format(k, v)
                     for k, v in el.attributes.items())


def _show_element(el, indent=''):
    if hasattr(el, 'tagName'):
        print(indent + el.tagName + ' - ' + _show_attrs(el))
    for child in el.childNodes:
        _show_element(child, indent + '  ')


def _is_paragraph(el):
    return el.tagName == 'text:p'


# -----------------------------------------------------------------------------
# Style-related utility functions
# -----------------------------------------------------------------------------

_STYLE_NAME = ('urn:oasis:names:tc:opendocument:xmlns:style:1.0',
               'display-name')


def _style_name(el):
    """Return the name of a style element."""
    return el.attributes.get(_STYLE_NAME, '').strip()


def _create_style(name, family=None, **kwargs):
    """Helper function for creating a new style."""
    style = Style(name=name, family=family)
    style.addElement(TextProperties(**kwargs))
    return style


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


def default_styles():
    """Generate default ODF styles."""

    styles = {}

    def _add_style(name, **kwargs):
        styles[name] = _create_style(name, **kwargs)

    _add_style('heading-1',
               family='paragraph', fontsize='24pt', fontweight='bold')
    _add_style('heading-2',
               family='paragraph', fontsize='22pt', fontweight='bold')
    _add_style('heading-3',
               family='paragraph', fontsize='20pt', fontweight='bold')
    _add_style('heading-4',
               family='paragraph', fontsize='18pt', fontweight='bold')
    _add_style('heading-5',
               family='paragraph', fontsize='16pt', fontweight='bold')
    _add_style('heading-6',
               family='paragraph', fontsize='14pt', fontweight='bold')

    _add_style('code', family='paragraph', fontsize='12pt',
               fontname='Courier New', color='#333333')
    _add_style('quote', family='paragraph', fontsize='12pt',
               fontstyle='italic')

    _add_style('normal', family='text', fontsize='12pt')
    _add_style('italic', family='text', fontstyle='italic', fontsize='12pt')
    _add_style('bold', family='text', fontweight='bold', fontsize='12pt')

    _add_style('url', family='text', fontsize='12pt',
               fontweight='bold', fontname='Courier')
    _add_style('inline-code', family='text', fontsize='12pt',
               fontname='Courier New', color='#333333')

    styles['_numbered_list'] = _numbered_style()

    return styles


def load_styles(path):
    """Return a dictionary of all styles contained in an ODF document."""
    with load(path) as f:
        return {_style_name(style): style for style in f.styles.childNodes}


# -----------------------------------------------------------------------------
# ODF Document
# -----------------------------------------------------------------------------

class ODFDocument(object):

    """Default stylename ==> actual stylename mapping."""
    style_mapping = {}

    def __init__(self, styles=None):

        self._doc = OpenDocumentText()

        self._styles = {}  # Dictionary of current styles.
        self._containers = []  # Stack of currently-active containers.
        self._next_p_style = None  # Style of the next paragraph to be created.
        self._ordered = False  # Where we're currently in an ordered list.

        # Add default styles if necessary.
        if styles is None:
            self.add_styles(**default_styles())

    # Public methods
    # -------------------------------------------------------------------------

    def show(self):
        _show_element(self._doc.text)

    def save(self, path, overwrite=False):
        if op.exists(path):
            if overwrite:
                os.remove(path)
            else:
                raise IOError("The file does already exist, "
                              "use overwrite=True.")
        self._doc.save(path)

    # Style methods
    # -------------------------------------------------------------------------

    def add_styles(self, **styles):
        """Add ODF styles to the current document."""
        self._styles.update(styles)
        for stylename in sorted(styles):
            self._doc.styles.addElement(styles[stylename])

    def _get_style(self, default_name):
        """Return a style from its default name."""
        actual_name = self.style_mapping.get(default_name, default_name)
        if actual_name not in self._styles:
            assert RuntimeError("The style {0} ".format(actual_name) +
                                "doesn't exist.")
        return self._styles.get(actual_name, None)

    @property
    def styles(self):
        return self._styles

    def show_styles(self):
        pprint(self._styles)

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
                kwargs['stylename'] = self._get_style(kwargs['stylename'])
        return kwargs

    def _add_element(self, cls, **kwargs):
        """Add an element."""
        # Convert stylename strings to actual style elements.
        kwargs = self._replace_stylename(kwargs)
        el = cls(**kwargs)
        self._doc.text.addElement(el)

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

    def end_container(self, cancel=False):
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
        if stylename is None and self._next_p_style is not None:
            stylename = self._next_p_style
            self._next_p_style = None
        self.start_container(P, stylename=stylename)

    def end_paragraph(self):
        """End the current paragraph."""
        self.end_container()

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

    def code_line(self, line):
        """Add a code line."""
        self.text(line)

    def code(self, text):
        """Add a code block."""
        with self.paragraph(stylename='code'):
            lines = text.splitlines()
            for line in lines[:-1]:
                self.code_line(line)
                self.linebreak()
            self.code_line(lines[-1])

    def start_quote(self):
        """Start a block quote. Require a new paragraph afterwards."""
        self._next_p_style = 'quote'

    def end_quote(self):
        """End a block quote."""
        self._next_p_style = None

    # List methods
    # -------------------------------------------------------------------------

    def start_numbered_list(self):
        """Start a numbered list."""
        self._ordered = True
        self.start_container(List, stylename='_numbered_list')

    def end_numbered_list(self):
        """End a numbered list."""
        self.end_container()
        self._ordered = None

    def start_list(self):
        """Start a list."""
        self._ordered = False
        self.start_container(List)

    def end_list(self):
        """End a list."""
        self.end_container()

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

    def text(self, text, stylename='normal'):
        """Add text within the current container."""
        assert self._containers
        container = self._containers[-1]
        container.addElement(Span(stylename=stylename, text=text))

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

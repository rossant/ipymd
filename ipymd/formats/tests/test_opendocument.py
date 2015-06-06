# -*- coding: utf-8 -*-

"""Test ODF parser and reader."""

#------------------------------------------------------------------------------
# Imports
#------------------------------------------------------------------------------

from ...core.format_manager import format_manager, convert
from ...utils.utils import (_remove_output,
                            _remove_code_lang,
                            _remove_images,
                            _flatten_links,
                            _diff
                            )
from ._utils import (_test_reader, _test_writer,
                     _exec_test_file, _read_test_file)


#------------------------------------------------------------------------------
# Test ODF parser
#------------------------------------------------------------------------------

def _diff_trees(tree_0, tree_1):
    for ch_0, ch_1 in zip(tree_0.get('children', []),
                          tree_1.get('children', [])):
        if ch_0 != ch_1:
            print('****')
            print(ch_0)
            print(ch_1)
            return


def _test_generate():
    """Regenerate the ODF example documents."""
    for ex in ('ex1',
               'ex2',
               ):
        markdown = _read_test_file(ex, 'markdown')
        odf = convert(markdown, from_='markdown', to='opendocument')
        odf.save('examples/{0}.opendocument.odt'.format(ex))


def _process_md(md):
    for f in (_remove_code_lang,
              _remove_images,
              _flatten_links):
        md = f(md)
    return md


def _test_odf_reader(basename):
    """Check that (test cells) and (test contents ==> cells) are the same."""
    converted, expected = _test_reader(basename, 'opendocument')
    converted = _process_md(converted)
    expected = _process_md(expected)
    assert converted == expected


def _test_odf_writer(basename):
    """Check that (test contents) and (test cells ==> contents) are the same.
    """
    converted, expected = _test_writer(basename, 'opendocument')
    assert converted == expected


def _test_odf_odf(basename):
    """Check that the double conversion is the identity."""

    contents = _read_test_file(basename, 'opendocument')
    cells = convert(contents, from_='opendocument')
    converted = convert(cells, to='opendocument')
    assert contents.tree() == converted.tree()


def test_odf_reader():
    _test_odf_reader('ex1')
    _test_odf_reader('ex2')


def test_odf_writer():
    _test_odf_writer('ex1')
    _test_odf_writer('ex2')


def test_odf_odf():
    _test_odf_odf('ex1')
    _test_odf_odf('ex2')

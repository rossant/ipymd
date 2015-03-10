# -*- coding: utf-8 -*-

"""Test core."""

#------------------------------------------------------------------------------
# Imports
#------------------------------------------------------------------------------

import os.path as op
import shutil

from ..format_manager import FormatManager, format_manager
from ...utils.tempdir import TemporaryDirectory


#------------------------------------------------------------------------------
# Test core functions
#------------------------------------------------------------------------------

def load_mock(path):
    # Return a list of lines.
    with open(path, 'r') as f:
        return [line.rstrip() for line in f.readlines()[1:]]


def save_mock(path, contents):
    # contents is a list of lines.
    with open(path, 'w') as f:
        f.write('mock\n')
        f.write('\n'.join(contents))


class MockReader(object):
    def read(self, contents):
        # contents is a list of lines.
        return [{'cell_type': 'markdown',
                 'source': line} for line in contents]


class MockWriter(object):
    def __init__(self):
        self.contents = []

    def write(self, cell):
        # contents is a list of lines.
        if cell['cell_type'] == 'markdown':
            self.contents.append(cell['source'])


def test_format_manager():
    fm = format_manager()
    fm.register(name='mock',
                reader=MockReader,
                writer=MockWriter,
                file_extension='.mock',
                load=load_mock,
                save=save_mock)

    contents = ['line 1', 'line 2', 'line 3']

    with TemporaryDirectory() as tempdir:
        path = op.join(tempdir, 'test.mock')
        fm.save(path, contents)

        # Test the custom load/save functions.
        loaded = fm.load(path)
        assert loaded == contents

        fm.save(path, loaded)
        with open(path, 'r') as f:
            assert f.read() == 'mock\nline 1\nline 2\nline 3'

        # Test the conversion from/to ipymd cells.
        cells = fm.convert(contents, from_='mock')
        assert cells == [{'cell_type': 'markdown',
                          'source': line} for line in contents]
        assert fm.convert(cells, to='mock') == contents

    fm.unregister('mock')

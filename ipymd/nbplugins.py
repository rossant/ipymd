"""A contents manager that uses the local file system for storage."""

# Copyright (c) IPython Development Team.
# Distributed under the terms of the Modified BSD License.

import io
import os

from tornado import web

from IPython import nbformat
from IPython.html.services.contents.filemanager import FileContentsManager
from IPython.utils.io import atomic_writing

from .converters import nb_to_markdown, markdown_to_nb

class IPymdContentsManager(FileContentsManager):
    code_wrap = None

    def _notebook_model(self, path, content=True):
        model = self._base_model(path)
        model['type'] = 'notebook'
        if content:
            os_path = self._get_os_path(path)
            with self.open(os_path, 'r', encoding='utf-8') as f:
                try:
                    ####### this has changed
                    # nb = nbformat.read(f, as_version=4)
                    nb = markdown_to_nb(f.read())
                except Exception as e:
                    raise web.HTTPError(400, u"Unreadable Notebook: %s %r" % (os_path, e))
            self.mark_trusted_cells(nb, path)
            model['content'] = nb
            model['format'] = 'json'
            self.validate_notebook_model(model)
        return model

    def get(self, path, content=True, type=None, format=None):
        path = path.strip('/')

        if not self.exists(path):
            raise web.HTTPError(404, u'No such file or directory: %s' % path)

        os_path = self._get_os_path(path)
        if os.path.isdir(os_path):
            if type not in (None, 'directory'):
                raise web.HTTPError(400,
                                u'%s is a directory, not a %s' % (path, type), reason='bad type')
            model = self._dir_model(path, content=content)
        ####### this has changed
        # elif type == 'notebook' or (type is None and path.endswith('.md')):
        elif type == 'notebook' or (type is None and (path.endswith('.ipynb')
                                                      or path.endswith('.md'))
                                    ):
            model = self._notebook_model(path, content=content)
        else:
            if type == 'directory':
                raise web.HTTPError(400,
                                u'%s is not a directory', reason='bad type')
            model = self._file_model(path, content=content, format=format)
        return model

    def _save_notebook(self, os_path, model, path=''):
        """Save a notebook model to a Markdown file."""
        md = nb_to_markdown(model['content'], code_wrap=self.code_wrap)
        with self.atomic_writing(os_path, encoding='utf-8') as f:
            f.write(md)

    def check_and_sign(self, nb, path=''):
        self.notary.sign(nb)

    def mark_trusted_cells(self, nb, path=''):
        self.notary.mark_cells(nb, True)

class MarkdownContentsManager(IPymdContentsManager):
    """Code cells are wrapped by ```."""
    code_wrap = 'markdown'

class AtlasContentsManager(IPymdContentsManager):
    "Code cells are wrapped by special <pre> tag."""
    code_wrap = 'html'

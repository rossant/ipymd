"""A contents manager that uses the local file system for storage."""

# Copyright (c) IPython Development Team.
# Distributed under the terms of the Modified BSD License.

import io
import os

from tornado import web

from IPython import nbformat
from IPython.utils.io import atomic_writing

from .converters import nb_to_markdown, markdown_to_nb

class MarkdownManager(FileContentsManager):
    def _dir_model(self, path, content=True):
        # DONE: replaced 'json' by 'text'
        model = super(MarkdownManager, self)._dir_model(path, content=content)
        if content:
            model['format'] = 'text'
        return model

    def _notebook_model(self, path, content=True):
        """Open a .md notebook."""
        model = self._base_model(path)
        model['type'] = 'notebook'
        if content:
            os_path = self._get_os_path(path)
            with self.open(os_path, 'r', encoding='utf-8') as f:
                try:
                    nb = markdown_to_nb(f.read())
                except Exception as e:
                    raise web.HTTPError(400, u"Unreadable Notebook: %s %r" % (os_path, e))
            self.mark_trusted_cells(nb, path)
            model['content'] = nb
            model['format'] = 'text'
            self.validate_notebook_model(model)
        return model

    def get(self, path, content=True, type=None, format=None):
        # DONE: replaced ipynb by md
        model = super(MarkdownManager, self).get(path, content=content,
                                                 type=type, format=format)
        path = path.strip('/')
        if (type is None and path.endswith('.md')):
            model = self._notebook_model(path, content=content)
        return model

    def _save_notebook(self, os_path, model, path=''):
        """Save a notebook model to a Markdown file."""

        # Save the notebook file
        md = nb_to_markdown(model['content'])

        # self.check_and_sign(nb, path)

        with self.atomic_writing(os_path, encoding='utf-8') as f:
            f.write(md)

    def restore_checkpoint(self, checkpoint_id, path):
        """restore a file to a checkpointed state"""
        path = path.strip('/')
        self.log.info("restoring %s from checkpoint %s", path, checkpoint_id)
        nb_path = self._get_os_path(path)
        cp_path = self.get_checkpoint_path(checkpoint_id, path)
        if not os.path.isfile(cp_path):
            self.log.debug("checkpoint file does not exist: %s", cp_path)
            raise web.HTTPError(404,
                u'checkpoint does not exist: %s@%s' % (path, checkpoint_id)
            )
        # ensure notebook is readable (never restore from an unreadable notebook)
        if cp_path.endswith('.md'):
            with self.open(cp_path, 'r', encoding='utf-8') as f:
                markdown_to_nb(f.read())
        self.log.debug("copying %s -> %s", cp_path, nb_path)
        with self.perm_to_403():
            self._copy(cp_path, nb_path)

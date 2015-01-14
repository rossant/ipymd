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
    add_prompt = None

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
        md = nb_to_markdown(model, code_wrap=self.code_wrap,
                            add_prompt=self.add_prompt)
        with self.atomic_writing(os_path, encoding='utf-8') as f:
            f.write(md)

    def new_untitled(self, path='', type='', ext=''):
        path = path.strip('/')
        if not self.dir_exists(path):
            raise HTTPError(404, 'No such directory: %s' % path)

        model = {}
        if type:
            model['type'] = type

        if ext == '.md':
            model.setdefault('type', 'notebook')
        else:
            model.setdefault('type', 'file')

        insert = ''
        if model['type'] == 'directory':
            untitled = self.untitled_directory
            insert = ' '
        elif model['type'] == 'notebook':
            untitled = self.untitled_notebook
            ext = '.md'
        elif model['type'] == 'file':
            untitled = self.untitled_file
        else:
            raise HTTPError(400, "Unexpected model type: %r" % model['type'])

        name = self.increment_filename(untitled + ext, path, insert=insert)
        path = u'{0}/{1}'.format(path, name)
        return self.new(model, path)

    def new(self, model=None, path=''):
        path = path.strip('/')
        if model is None:
            model = {}

        if path.endswith('.md'):
            model.setdefault('type', 'notebook')
        else:
            model.setdefault('type', 'file')

        # no content, not a directory, so fill out new-file model
        if 'content' not in model and model['type'] != 'directory':
            if model['type'] == 'notebook':
                model['content'] = new_notebook()
                model['format'] = 'json'
            else:
                model['content'] = ''
                model['type'] = 'file'
                model['format'] = 'text'

        model = self.save(model, path)
        return model

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


    def check_and_sign(self, nb, path=''):
        self.notary.sign(nb)

    def mark_trusted_cells(self, nb, path=''):
        self.notary.mark_cells(nb, True)

class MarkdownContentsManager(IPymdContentsManager):
    """Code cells are wrapped by ```."""
    code_wrap = 'markdown'
    add_prompt = False

class MarkdownOutputContentsManager(IPymdContentsManager):
    """Code cells are wrapped by ```, and code output + input prompt '>'."""
    code_wrap = 'markdown'
    add_prompt = True

class AtlasContentsManager(IPymdContentsManager):
    "Code cells are wrapped by special <pre> tag."""
    code_wrap = 'atlas'
    add_prompt = False

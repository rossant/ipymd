# -*- coding: utf-8 -*-

"""Notebook contents manager."""

#------------------------------------------------------------------------------
# Imports
#------------------------------------------------------------------------------

import io
import os

from tornado import web

from IPython import nbformat
from IPython.config.configurable import Configurable
from IPython.utils.traitlets import Unicode, Bool
from IPython.html.services.contents.filemanager import FileContentsManager
from IPython.utils.io import atomic_writing

from .scripts import nb_to_markdown, markdown_to_nb


#------------------------------------------------------------------------------
# MarkdownContentsManager
#------------------------------------------------------------------------------

class MarkdownContentsManager(FileContentsManager, Configurable):
    code_wrap = Unicode('markdown', config=True)
    add_prompt = Bool(True, config=True)

    def get(self, path, content=True, type=None, format=None):
        """ Takes a path for an entity and returns its model
        Parameters
        ----------
        path : str
            the API path that describes the relative path for the target
        content : bool
            Whether to include the contents in the reply
        type : str, optional
            The requested type - 'file', 'notebook', or 'directory'.
            Will raise HTTPError 400 if the content doesn't match.
        format : str, optional
            The requested format for file contents. 'text' or 'base64'.
            Ignored if this returns a notebook or directory model.
        Returns
        -------
        model : dict
            the contents model. If content=True, returns the contents
            of the file or directory as well.
        """
        path = path.strip('/')

        if not self.exists(path):
            raise web.HTTPError(404, u'No such file or directory: %s' % path)

        os_path = self._get_os_path(path)
        if os.path.isdir(os_path):
            if type not in (None, 'directory'):
                raise web.HTTPError(400,
                                u'%s is a directory, not a %s' % (path, type), reason='bad type')
            model = self._dir_model(path, content=content)
        elif type == 'notebook' or (type is None and
                                    (path.endswith('.ipynb') or
                                     path.endswith('.md'))):  # NEW
            model = self._notebook_model(path, content=content)
        else:
            if type == 'directory':
                raise web.HTTPError(400,
                                u'%s is not a directory', reason='bad type')
            model = self._file_model(path, content=content, format=format)
        return model

    def _read_notebook(self, os_path, as_version=4):
        """Read a notebook from an os path."""
        with self.open(os_path, 'r', encoding='utf-8') as f:
            try:
                return markdown_to_nb(f.read())  # NEW
            except Exception as e:
                raise HTTPError(
                    400,
                    u"Unreadable Notebook: %s %r" % (os_path, e),
                )

    def save(self, model, path=''):
        """Save the file model and return the model with no content."""
        path = path.strip('/')

        if 'type' not in model:
            raise web.HTTPError(400, u'No file type provided')
        if 'content' not in model and model['type'] != 'directory':
            raise web.HTTPError(400, u'No file content provided')

        self.run_pre_save_hook(model=model, path=path)

        os_path = self._get_os_path(path)
        self.log.debug("Saving %s", os_path)
        try:
            if model['type'] == 'notebook':
                # nb = nbformat.from_dict(model['content'])
                # self.check_and_sign(nb, path)
                # self._save_notebook(os_path, nb)
                md = nb_to_markdown(model['content']) # NEW
                self._save_file(os_path, md, 'text')
                # One checkpoint should always exist for notebooks.
                if not self.checkpoints.list_checkpoints(path):
                    self.create_checkpoint(path)
            elif model['type'] == 'file':
                # Missing format will be handled internally by _save_file.
                self._save_file(os_path, model['content'], model.get('format'))
            elif model['type'] == 'directory':
                self._save_directory(os_path, model, path)
            else:
                raise web.HTTPError(400, "Unhandled contents type: %s" % model['type'])
        except web.HTTPError:
            raise
        except Exception as e:
            self.log.error(u'Error while saving file: %s %s', path, e, exc_info=True)
            raise web.HTTPError(500, u'Unexpected error while saving file: %s %s' % (path, e))

        validation_message = None
        if model['type'] == 'notebook':
            self.validate_notebook_model(model)
            validation_message = model.get('message', None)

        model = self.get(path, content=False)
        if validation_message:
            model['message'] = validation_message

        self.run_post_save_hook(model=model, os_path=os_path)

        return model


    # def _notebook_model(self, path, content=True):
    #     model = self._base_model(path)
    #     model['type'] = 'notebook'
    #     if content:
    #         os_path = self._get_os_path(path)
    #         with self.open(os_path, 'r', encoding='utf-8') as f:
    #             try:
    #                 ####### this has changed compared to IPython
    #                 nb = markdown_to_nb(f.read())
    #             except Exception as e:
    #                 raise web.HTTPError(400, u"Unreadable Notebook: %s %r" % (os_path, e))
    #         self.mark_trusted_cells(nb, path)
    #         model['content'] = nb
    #         model['format'] = 'json'
    #         self.validate_notebook_model(model)
    #     return model

    # def get(self, path, content=True, type=None, format=None):
    #     path = path.strip('/')

    #     if not self.exists(path):
    #         raise web.HTTPError(404, u'No such file or directory: %s' % path)

    #     os_path = self._get_os_path(path)
    #     if os.path.isdir(os_path):
    #         if type not in (None, 'directory'):
    #             raise web.HTTPError(400,
    #                             u'%s is a directory, not a %s' % (path, type), reason='bad type')
    #         model = self._dir_model(path, content=content)
    #     ####### this has changed compared to IPython
    #     elif type == 'notebook' or (type is None and (path.endswith('.ipynb')
    #                                                   or path.endswith('.md'))
    #                                 ):
    #         model = self._notebook_model(path, content=content)
    #     else:
    #         if type == 'directory':
    #             raise web.HTTPError(400,
    #                             u'%s is not a directory', reason='bad type')
    #         model = self._file_model(path, content=content, format=format)
    #     return model

    # def _save_notebook(self, os_path, model, path=''):
    #     """Save a notebook model to a Markdown file."""
    #     md = nb_to_markdown(model, code_wrap=self.code_wrap,
    #                         add_prompt=self.add_prompt)
    #     with self.atomic_writing(os_path, encoding='utf-8') as f:
    #         f.write(md)

    # def new_untitled(self, path='', type='', ext=''):
    #     path = path.strip('/')
    #     if not self.dir_exists(path):
    #         raise HTTPError(404, 'No such directory: %s' % path)

    #     model = {}
    #     if type:
    #         model['type'] = type

    #     if ext == '.md':
    #         model.setdefault('type', 'notebook')
    #     else:
    #         model.setdefault('type', 'file')

    #     insert = ''
    #     if model['type'] == 'directory':
    #         untitled = self.untitled_directory
    #         insert = ' '
    #     elif model['type'] == 'notebook':
    #         untitled = self.untitled_notebook
    #         ext = '.md'
    #     elif model['type'] == 'file':
    #         untitled = self.untitled_file
    #     else:
    #         raise HTTPError(400, "Unexpected model type: %r" % model['type'])

    #     name = self.increment_filename(untitled + ext, path, insert=insert)
    #     path = u'{0}/{1}'.format(path, name)
    #     return self.new(model, path)

    # def new(self, model=None, path=''):
    #     path = path.strip('/')
    #     if model is None:
    #         model = {}

    #     if path.endswith('.md'):
    #         model.setdefault('type', 'notebook')
    #     else:
    #         model.setdefault('type', 'file')

    #     # no content, not a directory, so fill out new-file model
    #     if 'content' not in model and model['type'] != 'directory':
    #         if model['type'] == 'notebook':
    #             model['content'] = new_notebook()
    #             model['format'] = 'json'
    #         else:
    #             model['content'] = ''
    #             model['type'] = 'file'
    #             model['format'] = 'text'

    #     model = self.save(model, path)
    #     return model

    # def restore_checkpoint(self, checkpoint_id, path):
    #     """restore a file to a checkpointed state"""
    #     path = path.strip('/')
    #     self.log.info("restoring %s from checkpoint %s", path, checkpoint_id)
    #     nb_path = self._get_os_path(path)
    #     cp_path = self.get_checkpoint_path(checkpoint_id, path)
    #     if not os.path.isfile(cp_path):
    #         self.log.debug("checkpoint file does not exist: %s", cp_path)
    #         raise web.HTTPError(404,
    #             u'checkpoint does not exist: %s@%s' % (path, checkpoint_id)
    #         )
    #     # ensure notebook is readable (never restore from an unreadable notebook)
    #     if cp_path.endswith('.md'):
    #         with self.open(cp_path, 'r', encoding='utf-8') as f:
    #             markdown_to_nb(f.read())
    #     self.log.debug("copying %s -> %s", cp_path, nb_path)
    #     with self.perm_to_403():
    #         self._copy(cp_path, nb_path)


    # def check_and_sign(self, nb, path=''):
    #     self.notary.sign(nb)

    # def mark_trusted_cells(self, nb, path=''):
    #     self.notary.mark_cells(nb, True)


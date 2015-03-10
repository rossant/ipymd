# -*- coding: utf-8 -*-

"""Notebook contents manager."""

#------------------------------------------------------------------------------
# Imports
#------------------------------------------------------------------------------

import io
import os
import os.path as op

from tornado import web

from IPython import nbformat
from IPython.config.configurable import Configurable
from IPython.utils.traitlets import Unicode, Bool
from IPython.html.services.contents.filemanager import FileContentsManager

from .format_manager import convert, format_manager
from ipymd.ext.six.moves.urllib.error import HTTPError


#------------------------------------------------------------------------------
# MarkdownContentsManager
#------------------------------------------------------------------------------

def _file_extension(os_path):
    return op.splitext(os_path)[1]


class IPymdContentsManager(FileContentsManager, Configurable):
    format = Unicode('markdown', config=True)

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

        # File extension of the chosen format.
        file_extension = format_manager().file_extension(self.format)

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
                                     path.endswith(file_extension))):  # NEW
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

                # NEW
                file_ext = _file_extension(os_path)
                if file_ext == '.ipynb':
                    return nbformat.read(f, as_version=as_version)
                else:
                    return convert(os_path, from_=self.format, to='notebook')

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

                # NEW
                file_ext = _file_extension(os_path)
                if file_ext == '.ipynb':
                    nb = nbformat.from_dict(model['content'])
                    self.check_and_sign(nb, path)
                    self._save_notebook(os_path, nb)
                else:

                    contents = convert(model['content'],
                                       from_='notebook',
                                       to=self.format)

                    # Save a text file.
                    if (format_manager().file_type(self.format) in
                        ('text', 'json')):
                        self._save_file(os_path, contents, 'text')
                    # Save to a binary file.
                    else:
                        format_manager().save(os_path, contents,
                                              name=self.format,
                                              overwrite=True)

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

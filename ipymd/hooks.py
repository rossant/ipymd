from .converters import nb_to_markdown

def save_to_markdown(model, path=None, contents_manager=None):
    """Save to markdown when saving a notebook."""
    if model['type'] != 'notebook':
        return
    # only run on nbformat v4
    if model['content']['nbformat'] != 4:
        return
    path_md = path.replace('.ipynb', '.md')
    os_path_md = contents_manager._get_os_path(path_md)
    os_path_nb = contents_manager._get_os_path(path)

    nb_to_markdown(os_path_nb, os_path_md)

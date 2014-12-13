import os
import os.path as op
from converters import nb_to_markdown, markdown_to_nb

dir = op.dirname(os.path.realpath(__file__))
path_ipynb = op.join(dir, '../notebooks/notebook_example.ipynb')
path_md = op.join(dir, '../notebooks/notebook_example.md')
path_ipynb2 = op.join(dir, '../notebooks/notebook_example_converted.ipynb')
path_md2 = op.join(dir, '../notebooks/notebook_example_converted.md')

nb_to_markdown(path_ipynb, path_md)
markdown_to_nb(path_md, path_ipynb2)
nb_to_markdown(path_ipynb2, path_md2)

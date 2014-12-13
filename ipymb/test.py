import os
import os.path as op
from converters import nb_to_markdown

dir = op.dirname(os.path.realpath(__file__))
path = op.join(dir, '../notebooks/notebook_example.ipynb')

nb_to_markdown(path, path.replace('.ipynb', '.md'))

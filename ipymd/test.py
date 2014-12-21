import os
import os.path as op
from pprint import pprint
from ipymd.converters import nb_to_markdown, markdown_to_nb

dir = op.dirname(os.path.realpath(__file__))
path_ipynb = op.join(dir, '../notebooks/ipynb.ipynb')
path_md = op.join(dir, '../notebooks/md.md')

# nb_to_markdown(path_ipynb, path_md)

with open(path_md, 'r') as f:
    md = f.read()

nb = markdown_to_nb(md)

md2 = nb_to_markdown(nb, code_wrap='html')

print(md2)


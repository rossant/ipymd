import os
import os.path as op
from pprint import pprint
from ipymd.converters import nb_to_markdown, markdown_to_nb, process_latex


dir = op.dirname(os.path.realpath(__file__))

code_wrap = 'atlas'  # 'atlas' or 'markdown'
path_md = op.join(dir, '../notebooks/test_%s.md' % code_wrap)

add_prompt = True

with open(path_md, 'r') as f:
    md = f.read()

nb = markdown_to_nb(md)
pprint(nb)

print('----------')

md2 = nb_to_markdown(nb, code_wrap=code_wrap, add_prompt=add_prompt)
print(md2)

print('----------')

nb = markdown_to_nb(md2)
pprint(nb)

print('----------')

md2 = nb_to_markdown(nb, code_wrap=code_wrap, add_prompt=add_prompt)
print(md2)

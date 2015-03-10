# List of ipymd cells expected for this example.
output = [

    {'cell_type': 'markdown',
     'source': '# Test notebook'},

    {'cell_type': 'markdown',
     'source': 'This is a text notebook. Here *are* some **rich text**, '
               '`code`, $\\pi\\simeq 3.1415$ equations.'},

    {'cell_type': 'markdown',
     'source': 'Another equation:'},

    {'cell_type': 'markdown',
     'source': '$$\\sum_{i=1}^n x_i$$'},

    {'cell_type': 'markdown',
     'source': 'Python code:'},

    {'cell_type': 'code',
     'input': '# some code in python\ndef f(x):\n    y = x * x\n    return y',
     'output': ''},

    {'cell_type': 'markdown',
     'source': 'Random code:'},

    {'cell_type': 'markdown',
     'source': '```javascript\nconsole.log("hello" + 3);\n```'},

    {'cell_type': 'markdown',
     'source': 'Python code:'},

    {'cell_type': 'code',
     'input': 'import IPython\nprint("Hello world!")',
     'output': 'Hello world!'},

    {'cell_type': 'code',
     'input': '2*2', 'output': '4'},

    {'cell_type': 'code',
     'input': 'def decorator(f):\n    return f',
     'output': ''},

    {'cell_type': 'code',
     'input': '@decorator\ndef f(x):\n    pass\n3*3',
     'output': '9'},

    {'cell_type': 'markdown',
     'source': 'some text'},

    {'cell_type': 'code',
     'input': 'print(4*4)', 'output': '16'},

    {'cell_type': 'code',
     'input': "%%bash\necho 'hello'", 'output': 'hello'},

    {'cell_type': 'markdown',
     'source': 'An image:'},

    {'cell_type': 'markdown',
     'source': '![Hello '
               'world](http://wristgeek.com/wp-content/uploads/2014/09/'
               'hello_world.png)'},

    {'cell_type': 'markdown',
     'source': '### Subtitle'},

    {'cell_type': 'markdown',
     'source': 'a list'},

    {'cell_type': 'markdown',
     'source': '* One [small](http://www.google.fr) link!\n'
               '* Two\n'
               '  * 2.1\n'
               '  * 2.2\n'
               '* Three'},

    {'cell_type': 'markdown',
     'source': 'and'},

    {'cell_type': 'markdown',
     'source': '1. Un\n2. Deux'},

    {'cell_type': 'code',
     'input': 'import numpy as np\n'
              'import matplotlib.pyplot as plt\n'
              '%matplotlib inline',
     'output': ''},

    {'cell_type': 'code',
     'input': "plt.imshow(np.random.rand(5,5,4), interpolation='none');",
     'output': ''},

    {'cell_type': 'markdown',
     'source': "> TIP (a block quote): That's all folks.\n> Last line."},

    {'cell_type': 'markdown', 'source': 'Last paragraph.'}

]

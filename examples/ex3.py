# List of ipymd cells expected for this example.
output = [

    {'cell_type': 'markdown',
     'source': '# Header',
     'metadata': {'slideshow': {'slide_type': 'slide'}}},

    {'cell_type': 'markdown',
     'source': 'A paragraph.',
     'metadata': {'slideshow': {'slide_type': 'slide'}}},

    {'cell_type': 'markdown',
     'source': 'Python code:',
     'metadata': {'ipymd': {'empty_meta': True}}},

    {'cell_type': 'code',
     'input': 'print("Hello world!")',
     'output': 'Hello world!',
     'metadata': {'slideshow': {'slide_type': 'fragment'}}},

    {'cell_type': 'markdown',
     'source': 'JavaScript code:',
     'metadata': {'slideshow': {'slide_type': 'skip'}}},

    {'cell_type': 'markdown',
     'source': '```javascript\nconsole.log("Hello world!");\n```',
     'metadata': {'slideshow': {'slide_type': 'skip'}}},

]

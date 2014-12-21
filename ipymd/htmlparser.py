"""Parse HTML and LaTeX equations from Atlas HTML5."""
from html.parser import HTMLParser
from html.entities import name2codepoint

class MyHTMLParser(HTMLParser):
    def __init__(self, *args, **kwargs):
        super(MyHTMLParser, self).__init__(*args, **kwargs)
        self.is_code = False
        self.is_math = False
        self.data = ''

    def handle_starttag(self, tag, attrs):
        if tag == 'pre' and ('data-type', 'programlisting') in attrs:
            self.is_code = True
        elif tag == 'span' and ('data-type', 'tex') in attrs:
            self.is_math = True

    def handle_data(self, data):
        if self.is_code:
            self.data += data
        elif self.is_math:
            self.data += data

def get_html_contents(html):
    parser = MyHTMLParser()
    parser.feed(html)
    if parser.is_code:
        return ('code', parser.data.strip())
    elif parser.is_math:
        return ('math', parser.data.strip())

if __name__ == '__main__':
    math = """<span class="math-tex" data-type="tex">\(x = {-b \pm \sqrt{b^2-4ac} \over 2a}\)</span>"""
    code = """<pre data-code-language="python" data-executable="true" data-type="programlisting">
def f():
    print('hello world!')
    print('hello world, again!')

print(f)    # hello world
</pre>
"""

    print(get_html_contents("<span>HELLO</span>"))
    print(get_html_contents(math)[1])
    print(get_html_contents(code)[1])

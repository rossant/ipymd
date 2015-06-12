[![Build Status](https://travis-ci.org/rossant/ipymd.svg?branch=travis)](https://travis-ci.org/rossant/ipymd)
[![Coverage Status](https://coveralls.io/repos/rossant/ipymd/badge.svg)](https://coveralls.io/r/rossant/ipymd)

# Replace .ipynb by .md in the IPython notebook

The goal of ipymd is to replace `.ipynb` notebook files like:

```json
{
 "cells": [
  {
   "cell_type": "markdown",
   "source": [
    "Here is some Python code:"
   ]
  },
  {
   "cell_type": "code",
   "outputs": [
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "Hello world!\n"
     ]
    }
   ],
   "source": [
    "print(\"Hello world!\")"
   ]
  },
  ...
```

by:

    Here is some Python code:

    ```python
    >>> print("Hello world!")
    Hello world!
    ```

The JSON `.ipymd` are removed out from the equation, and the conversion happens on-the-fly. The IPython notebook becomes an interactive Markdown text editor!

A drawback is that you loose metadata, prompt numbers, and images (for now).

This is useful when you write technical documents, blog posts, books, etc.

![image](https://cloud.githubusercontent.com/assets/1942359/5570181/f656a484-8f7d-11e4-8ec2-558d022b13d3.png)

## Why?

### IPython notebook

Pros:

* Excellent UI for executing code interactively *and* writing text

Cons:

* .ipynb not git-friendly
* Cannot easily edit in a text editor
* Cannot easily edit on GitHub's web interface


### Markdown

Pros:

* Simple ASCII format to write code and text
* Can easily edit in a text editor
* Can easily edit on GitHub's web interface
* Git-friendly

Cons:

* No UI to execute code interactively


### ipymd

All pros of IPython notebook and Markdown, no cons!


## How it works

* Write in Markdown in `document.md`
    * Either in a text editor (convenient when working on text)
    * Or in the notebook (convenient when writing code examples)
* Only the Markdown cells and code cells are saved in the file
* Collaborators can work on the Markdown document using GitHub's web interface.
* By convention, a **notebook code cell** is equivalent to a **Markdown code block with explicit `python` syntax highlighting**:

  ```
  >>> print("Hello world")
  Hello world
  ```

* The back-and-forth conversion is not strictly the identity:
    * Extra line breaks in Markdown are discarded
    * Text output and standard output are combined into a single text output (stdout lines first, output lines last)


## Caveats

**WARNING**: use this library at your own risks, backup your data, and version-control your notebooks and Markdown files!

* Renaming doesn't work yet (issue #4)
* New notebook doesn't work yet (issue #5)
* Only nbformat v4 is supported currently (IPython 3.0)


## Installation

1. Install ipymd:

    To install the latest release version:

    ```shell
    pip install ipymd
    ```

    Alternatively, to install the development version:

    ```shell
    pip install git+https://github.com/rossant/ipymd
    ```

2. **Optional:**
    To interact with `.ipynb` files:

    ```shell
    pip install ipython[notebook]
    ```

    To interact with `.odt` files:

    ```shell
    pip install git+https://github.com/eea/odfpy
    ```

3. Add this to your `ipython_notebook_config.py` file:

    ```python
    c.NotebookApp.contents_manager_class = 'ipymd.IPymdContentsManager'
    ```

4. Now, you can open `.md` files in the notebook.


## Formats

ipymd uses a modular architecture that lets you define new formats. The following formats are currently implemented:

* IPython notebook (`.ipynb`)
* Markdown (`.md`)
    * `c.IPymdContentsManager.format = 'markdown'`
* [O'Reilly Atlas](http://odewahn.github.io/publishing-workflows-for-jupyter/#1)  (`.md` with special HTML tags for code and mathematical equations)
    * `c.IPymdContentsManager.format = 'atlas'`
* Python (`.py`): code cells are delimited by double line breaks. Markdown cells = Python comments. [TODO: this doesn't work well, see #28 and #31]
* Opendocument (`.odt`). You need to install the [development version of odfpy](https://github.com/eea/odfpy/).

You can convert from any supported format to any supported format. This works by converting to an intermediate format that is basically a list of notebook cells.

### ipymd cells

An **ipymd cell** is a Python dictionary with the following fields:

* `cell_type`: `markdown` or `code`
* `input`: a string with the code input (code cell only)
* `output`: a string with the text output and stdout (code cell only)
* `source`: a string containing Markdown markup (markdown cell only)


### Customize the Markdown format

You can customize the exact way the notebook is converted from/to Markdown by deriving from `BaseMarkdownReader` or `MarkdownReader` (idem with writers). Look at `ipymd/formats/markdown.py`.


### Implement your own format

You can also implement your own format by following these instructions:

* Create a `MyFormatReader` class that implements:
    * `self.read(contents)`: yields ipymd cells from a `contents` string
* Create a `MyFormatWriter` class that implements:
    * `self.write(cell)`: append an ipymd cell
    * `self.contents`: return the contents as a string
* To activate this format, call this:

  ```python
  from ipymd import format_manager
  format_manager().register('my_format',
                            reader=MyFormatReader,
                            writer=MyFormatWriter,
                            file_extension='.md',  # or anything else
                            file_type='text',  # or JSON
                            )
  ```

* Now you can convert contents: `ipymd.convert(contents, from_='notebook', to='my_format')` or any other combination.
* To further integrate your format in ipymd, create a `ipymd/formats/my_format.py` file.
* Put your reader and writer class in there, as well as a global variable (needs to end with `FORMAT`):

  ```python
    MY_FORMAT = dict(
      name='markdown',
      reader=MyFormatReader,
      writer=MyFormatWriter,
      file_extension='.md',
      file_type='text',
  )
  ```
* Import this file in `ipymd/formats/__init__.py`.
* Add `c.IPymdContentsManager.format = 'my_format'` to your IPython notebook config file.
* Add some unit tests in `ipymd/formats/tests`.
* Propose a PR!

Look at the existing format implementations for more details.

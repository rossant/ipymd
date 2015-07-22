[![Build Status](https://travis-ci.org/rossant/ipymd.svg?branch=travis)](https://travis-ci.org/rossant/ipymd)
[![Coverage Status](https://coveralls.io/repos/rossant/ipymd/badge.svg)](https://coveralls.io/r/rossant/ipymd)

# Replace .ipynb with .md in the IPython Notebook

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
  }
  ...
  ]
}
```

with:

    Here is some Python code:

    ```python
    >>> print("Hello world!")
    Hello world!
    ```

The JSON `.ipynb` are removed from the equation, and the conversion happens on the fly. The IPython Notebook becomes an interactive Markdown text editor!

A drawback is that you lose prompt numbers and images (for now).

This is useful when you write technical documents, blog posts, books, etc.

![image](https://cloud.githubusercontent.com/assets/1942359/5570181/f656a484-8f7d-11e4-8ec2-558d022b13d3.png)

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

4. Now, you can open `.md` files in the Notebook.

## Why?

### IPython Notebook

Pros:

* Excellent UI for executing code interactively *and* writing text

Cons:

* `.ipynb` not git-friendly
* Cannot easily edit in a text editor
* Cannot easily edit on GitHub's web interface


### Markdown

Pros:

* Simple ASCII/Unicode format to write code and text
* Can easily edit in a text editor
* Can easily edit on GitHub's web interface
* Git-friendly

Cons:

* No UI to execute code interactively


### ipymd

All pros of IPython Notebook and Markdown, no cons!


## How it works

* Write in Markdown in `document.md`
    * Either in a text editor (convenient when working on text)
    * Or in the Notebook (convenient when writing code examples)
* Markdown cells, code cells and (optionally) notebook metadata are saved in
  the file
* Collaborators can work on the Markdown document using GitHub's web interface.
* By convention, a **notebook code cell** is equivalent to a **Markdown code block with explicit `python` syntax highlighting**:

  ```
  >>> print("Hello world")
  Hello world
  ```

* **Notebook metadata** can be specified in [YAML](http://yaml.org/) inside
  Jekyll-style [front-matter](http://jekyllrb.com/docs/frontmatter/) dashes
  at the beginning of a document:

  ```markdown
  ---
  kernelspec:
    name: some-non-native-kernel
  ---

  First cell content
  ```

  Native kernel metadata will be elided by default: non-python kernels haven't
  been tested yet, but support is planned.

* **Cell metadata** is specified with YAML stream documents with dashes and
  periods, such as to create slides:

  ```markdown
  # Previous slide

  ---
  slideshow:
    slide_type: slide
  ...

  # Some Slide Content
  ```

  > NOTE: You probably shouldn't use `---` to mean an `<hr/>`: `***`
  could be a suitable substitute.

* Null metadata (i.e. splitting a markdown cell) can be created with just
  three dashes. This is useful when adding slideshow notes or skipped cells.

  ```markdown
  A cell

  ---

  Another cell
  ```

* The back-and-forth conversion is not strictly the identity function:
    * Extra line breaks in Markdown are discarded
    * Text output and standard output are combined into a single text output (stdout lines first, output lines last)


## Caveats

**WARNING**: use this library at your own risks, backup your data, and version-control your notebooks and Markdown files!

* Renaming doesn't work yet (issue #4)
* New notebook doesn't work yet (issue #5)
* Only nbformat v4 is supported currently (IPython 3.0)


## Formats

ipymd uses a modular architecture that lets you define new formats. The following formats are currently implemented, and can be selected by modifying `~/.ipython/profile_<whichever>/ipython_notebook_config.py`:

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

* `cell_type`: `markdown`, `code` or `notebok_metadata` (if implemented)
* `input`: a string with the code input (code cell only)
* `output`: a string with the text output and stdout (code cell only)
* `source`: a string containing Markdown markup (markdown cell only)
* `metadata`: a dictionary containing cell (or notebook) metadata

### Kernel Metadata

By default, notebook metadata for the native kernel (usually `python2` or
`python3`) won't be written to markdown. Since ipymd doesn't yet support other
kernels, this doesn't matter much, but if you would like to pick a non-native
python kernel to be interpreted as the default for ipymd, and store
`kernelspec` and `language_info` for the other, you can add this to your
`ipython_notebook_config.py` file:
  * `c.IPymdContentsManager.default_kernel_name = 'python2'`

Or, to always remember all notebook-level metadata:
  * `c.IPymdContentsManager.verbose_metadata = True`

### Customize the Markdown format

You can customize the exact way the notebook is converted from/to Markdown by deriving from `BaseMarkdownReader` or `MarkdownReader` (idem with writers). Look at `ipymd/formats/markdown.py`.

### Implement your own format

You can also implement your own format by following these instructions:

* Create a `MyFormatReader` class that implements:
    * `self.read(contents)`: yields ipymd cells from a `contents` string
* Create a `MyFormatWriter` class that implements:
    * `self.write(cell)`: append an ipymd cell
      * (optional) `self.write_notebook_metadata(cell)`: write the notebook
        metadata dictionary
    * `self.contents`: return the contents as a string

* To activate this format, call this at Notebook launch time (not in a kernel!), perhaps in your `ipython_notebook_config.py`:

```python
  from ipymd import format_manager
  format_manager().register(
      name='my_format',
      reader=MyFormatReader,
      writer=MyFormatWriter,
      file_extension='.md',  # or anything else
      file_type='text',  # or JSON
  )
```

* Now you can convert contents: `ipymd.convert(contents, from_='notebook', to='my_format')` or any other combination.

### Contributing a new ipymd format
* To further integrate your format in ipymd, create a `ipymd/formats/my_format.py` file.
* Put your reader and writer class in there, as well as a top-level variable:

```python
  MY_FORMAT = dict(
      reader=MyFormatReader,
      writer=MyFormatWriter,
      file_extension='.md',
      file_type='text',
  )
```

* In `setup.py`, add this to `entry_points`:

```python
      ...
      entry_points={
          'ipymd.format': [
              ...
              'my_format=myformat:MY_FORMAT',
              ...
          ]
      }
```

  > Note that the `entry_point` name will be used by default. you may override
    it, if you like, but Don't Repeat Yourself.

* Add some unit tests in `ipymd/formats/tests`.
* Propose a PR!

Look at the existing format implementations for more details.


### Packaging a format
* If you want to be able to redistribute your format without adding it to ipymd proper (i.e. in-house or experimental), implement all your code in a real python module.
* Someplace easy to import, e.g. `myformat.py` or `myformat/__init__.py`, add:

```python
  MY_FORMAT = dict(
      reader=MyFormatReader,
      writer=MyFormatWriter,
      file_extension='.md',  # or anything else
      file_type='text',  # or JSON
  )
```

  and this to your `setup.py`:

```python
  ...
      entry_points={
          'ipymd.format': [
              'my_format=myformat:MY_FORMAT',
              ],
          },
  ...
```

  * Publish on pypi!
  * Your users will now be able to `pip install myformat`, then configure their Notebook to use your format with the name `my_format`.

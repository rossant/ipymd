[![Build Status](https://travis-ci.org/rossant/ipymd.svg?branch=travis)](https://travis-ci.org/rossant/ipymd)
[![Coverage Status](https://coveralls.io/repos/rossant/ipymd/badge.svg)](https://coveralls.io/r/rossant/ipymd)

# IPython notebook & Markdown

**Currently WIP, experimental project, use at your own risks**

Use Markdown `.md` documents instead of `.ipynb` files in the IPython notebook. You keep code input and outputs, but not plots, metadata, or prompt numbers. This is useful when you write technical documents, blog posts, books, etc.

![image](https://cloud.githubusercontent.com/assets/1942359/5570181/f656a484-8f7d-11e4-8ec2-558d022b13d3.png)

## Why?

### IPython notebook

Pros:

* Excellent UI for executing code interactively *and* writing text

Cons:

* nbformat not really git-friendly (JSON, contains the outputs by default)
* cannot easily edit in a text editor


### Markdown

Pros:

* Simple ASCII format to write code and text
* Can be edited in any text editor
* Git-friendly

Cons:

* No UI to execute code interactively

## Workflow

* Write contents (text and code) in a Markdown `document.md`
    * either in the notebook UI, as usual, with Markdown cells and code cells (useful when working on code)
    * or in a text editor, using Markdown (useful when working on text)
* Only the Markdown cells and code cells (input + text outputs for now) are saved in the file
* Collaborators can work on the Markdown document using GitHub (branches, pull requests...), they don't need IPython. They can do everything from the GitHub web interface.

### Details

* A notebook code cell = Markdown code block with explicit `python` syntax highlighting (i.e. ```` ```python ````)

  ```
  > print("Hello world")
  Hello world
  ```

* `md => nb => md` and `nb => md => nb` are not exactly the identity function:

    * extra line breaks are discarded
    * text output and text stdout ==> combined text output (stdout lines first, output lines last)


## Caveats

**WARNING**: this is an experimental module, there is a risk for data loss, so be careful!

* Renaming doesn't work yet (issue #4)
* New notebook doesn't work yet (issue #5)
* Only nbformat v4 is supported currently


## Installation

0. You need IPython 3.0 (or latest master).
1. Put this repo in your PYTHONPATH.
2. Add this in your `ipython_notebook_config.py` file:

    ```python
    c.NotebookApp.contents_manager_class = 'ipymd.MarkdownContentsManager'
    ```

3. Now, you can open `.md` files in the notebook.

### Atlas

[O'Reilly Atlas](http://odewahn.github.io/publishing-workflows-for-jupyter/#1) is also supported.

* Math equations are automatically replaced by `<span class="math-tex" data-type="tex">{equation}</span>` tags.
* Code inputs are replaced by `<pre data-code-language="{lang}" data-executable="true" data-type="programlisting">{code}</pre>` tags.

This is handled transparently in the notebook UI, i.e. you can keep writing math in `$$` and code in code cells or Markdown code blocks.

To use the Atlas format, put this in your config file:

```python
c.NotebookApp.contents_manager_class = 'ipymd.AtlasContentsManager'
```

## Code architecture

* An internal format is used, close, but not identical to nbformat: list of dicts (**ipymd cells**) with the following fields:
    * 'cell_type': 'markdown' or 'code'
    * 'input': a string with the code input
    * 'output': a string with the text output and stdout
    * 'source': contents of Markdown cells
* MarkdownReader parses a Markdown document with code taken from mistune, and generates a list of ipymd cells
* MarkdownWriter reads a list of ipymd cells and generates a Markdown documet
* NotebookReader reads an ipynb model and generates a list of ipymd cells
* NotebookWriter reads a list of ipymd cells and generates an IPython notebook model

The readers and writers can be specialized by deriving them. This is how Atlas support is implemented.

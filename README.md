# IPython notebook & Markdown

Combining the best of IPython notebook and Markdown for git-friendly technical book writing.

**tl; dr**: this **experimental** module replaces the JSON-based `.ipynb` format by Markdown `.md` documents (this is exactly Markdown, not a variant). You loose all metadata and code outputs, but you keep Markdown text and code. This is useful when you write technical documents, blog posts, books, etc.

## Rationale

### IPython notebook

Pros:

* Excellent UI for executing code interactively *and* writing text

Cons:

* nbformat not really git-friendly (JSON, contains the code output by default)
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
* Only the Markdown cells and input code cells are saved in the file
* Collaborators can work on the Markdown document using GitHub (branches, pull requests...), they don't need IPython. They can do everything from the GitHub web interface.


## CAVEATS

**WARNING**: this is an experimental module, there is a risk for data loss, so be careful!

* DO NOT RENAME YOUR .MD NOTEBOOKS IN THE NOTEBOOK UI


## Installation

0. You need IPython 3.0 (or latest master) (with PR #7278) and mistune.
1. Put this repo in your PYTHONPATH.
2. Add this in your `ipython_notebook_config.py` file:

    ```python
    c.NotebookApp.contents_manager_class = 'ipymd.MarkdownContentsManager'
    ```

3. Now, you can open `.md` files in the notebook.

There is also experiment support for O'Reilly Atlas in the `support-atlas` branch. Math equations are automatically replaced by special `<span>` tags, and code inputs are replaced by special `<pre>` tags. This is handled transparently in the notebook UI, i.e. you can keep writing math in `$$` and code in code cells or Markdown code blocks.

To use the Atlas format, put this instead in your config file:

```python
c.NotebookApp.contents_manager_class = 'ipymd.AtlasContentsManager'
```

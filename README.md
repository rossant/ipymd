# IPython notebook & Markdown

Combining the best of IPython notebook and Markdown for git-friendly technical book writing.

## IPython notebook

Pros:

* Excellent UI for executing code interactively *and* writing text

Cons:

* nbformat not really git-friendly (JSON, contains the code output by default)


## Markdown

Pros:

* Simple ASCII format to write code and text
* Git-friendly

Cons:

* No UI to execute code interactively


## ipymd

We propose a simple workflow to combine the best of both worlds.

* Git-friendly
* Write content in the notebook UI *or* in a text editor (Markdown)
* Only the text and code input are version-controlled (not the output)


## Workflow

* Write contents (text and code)
    * either in the notebook UI (useful when working on code)
    * or in a text editor (useful when working on text)
* When writing in the notebook, the contents are automatically exported to Markdown
* Only the Markdown documents are version controlled
* Collaborators can work on the Markdown document using GitHub (branches, pull requests...)
* The Markdown document is always up-to-date and can be exported to a notebook at any time for interactive code editing


## Components

Four components are needed:

1. [DONE] An ipynb ==> md converter
2. [DONE] An md ==> ipynb converter
3. [DONE] An IPython notebook plugin that automatically exports an ipynb to md upon saving
4. A git post-merge hook that automatically converts md documents to ipynb


## Installation

0. You need IPython 3.0 (or latest master) and mistune.
1. Put this repo in your PYTHONPATH.
2. Add this in your `ipython_notebook_config.py` file:

    ```python
    from ipymd.hooks import save_to_markdown
    c.FileContentsManager.pre_save_hook = save_to_markdown
    ```


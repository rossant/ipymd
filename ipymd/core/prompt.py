# -*- coding: utf-8 -*-

"""Prompt manager."""

#------------------------------------------------------------------------------
# Imports
#------------------------------------------------------------------------------

import re


#------------------------------------------------------------------------------
# Base Prompt manager
#------------------------------------------------------------------------------

def _to_lines(code):
    return [line.rstrip() for line in code.rstrip().splitlines()]


def _to_code(lines):
    return '\n'.join(line.rstrip() for line in lines)


def _add_line_prefix(lines, prefix):
    return [prefix + line for line in lines]


def _template_to_regex(template):
    regex = template
    # Escape special characters.
    for char in r'{}[]()+*?:-':
        regex = regex.replace(char, '\\' + char)
    regex = regex.replace(r'\{n\}', r'\d+')
    return regex


def _starts_with_regex(line, regex):
    """Return whether a line starts with a regex or not."""
    if not regex.startswith('^'):
        regex = '^' + regex
    reg = re.compile(regex)
    return reg.match(line)


class BasePromptManager(object):
    """Add and remove prompt from code cells."""

    input_prompt_template = ''  # may contain {n} for the input number
    output_prompt_template = ''

    input_prompt_regex = ''
    output_prompt_regex = ''

    def __init__(self):
        self.reset()
        if not self.input_prompt_regex:
            self.input_prompt_regex = _template_to_regex(
                self.input_prompt_template)
        if not self.output_prompt_regex:
            self.output_prompt_regex = _template_to_regex(
                self.output_prompt_template)

    def reset(self):
        self._number = 1

    def _replace_template(self, pattern, **by):
        if not by:
            by = dict(n=self._number)
        if '{n}' in pattern:
            return pattern.format(**by)
        else:
            return pattern

    @property
    def input_prompt(self):
        return self._replace_template(self.input_prompt_template)

    @property
    def output_prompt(self):
        return self._replace_template(self.output_prompt_template)

    def is_input(self, line):
        """Return whether a code line is an input, based on the input
        prompt."""
        return _starts_with_regex(line, self.input_prompt_regex)

    def split_input_output(self, text):
        """Split code into input lines and output lines, according to the
        input and output prompt templates."""
        lines = _to_lines(text)
        i = 0
        for line in lines:
            if _starts_with_regex(line, self.input_prompt_regex):
                i += 1
            else:
                break
        return lines[:i], lines[i:]

    def from_cell(self, input, output):
        """Convert input and output to code text with prompts."""
        raise NotImplementedError()

    def to_cell(self, code):
        """Convert code text with prompts to input and output."""
        raise NotImplementedError()


#------------------------------------------------------------------------------
# Simple prompt manager
#------------------------------------------------------------------------------

class SimplePromptManager(BasePromptManager):
    """No prompt number, same input prompt at every line, idem for output."""
    input_prompt_template = ''
    output_prompt_template = ''

    def from_cell(self, input, output):
        input_l = _to_lines(input)
        output_l = _to_lines(output)

        input_l = _add_line_prefix(input_l, self.input_prompt)
        output_l = _add_line_prefix(output_l, self.output_prompt)

        return _to_code(input_l) + '\n' + _to_code(output_l)

    def to_cell(self, code):
        input_l, output_l = self.split_input_output(code)

        n = len(self.input_prompt_template)
        input = _to_code([line[n:] for line in input_l])

        n = len(self.output_prompt_template)
        output = _to_code([line[n:] for line in output_l])

        return input.rstrip(), output.rstrip()


#------------------------------------------------------------------------------
# IPython prompt manager
#------------------------------------------------------------------------------

class IPythonPromptManager(BasePromptManager):
    input_prompt_template = 'In [{n}]: '
    input_prompt_regex = '(In \[\d+\]\: | {6,})'

    output_prompt_template = 'Out[{n}]: '

    def _add_prompt(self, lines, prompt):
        lines[:1] = _add_line_prefix(lines[:1], prompt)
        lines[1:] = _add_line_prefix(lines[1:], ' ' * len(prompt))
        return lines

    def from_cell(self, input, output=None):
        input_l = _to_lines(input)
        output_l = _to_lines(output)

        input_l = self._add_prompt(input_l, self.input_prompt)
        output_l = self._add_prompt(output_l, self.output_prompt)

        input_p = _to_code(input_l)
        output_p = _to_code(output_l)

        self._number += 1

        return input_p + '\n' + output_p

    def to_cell(self, text):
        input_l, output_l = self.split_input_output(text)

        m = _starts_with_regex(input_l[0], self.input_prompt_regex)
        assert m
        input_prompt = m.group(0)
        n_in = len(input_prompt)
        input_l = [line[n_in:] for line in input_l]
        input = _to_code(input_l)

        m = _starts_with_regex(output_l[0], self.output_prompt_regex)
        assert m
        output_prompt = m.group(0)
        n_out = len(output_prompt)
        output_l = [line[n_out:] for line in output_l]
        output = _to_code(output_l)

        return input, output


#------------------------------------------------------------------------------
# Python prompt manager
#------------------------------------------------------------------------------

class PythonPromptManager(SimplePromptManager):
    input_prompt_template = '>>> '
    second_input_prompt_template = '... '

    input_prompt_regex = r'>>>|\.\.\.'

    output_prompt_template = ''

    def from_cell(self, input, output):
        lines = _to_lines(input)
        first = self.input_prompt_template
        second = self.second_input_prompt_template

        lines_prompt = []
        prompt = first
        lock = False
        for line in lines:
            if line.startswith('%%'):
                lines_prompt.append(prompt + line)
                prompt = second
                lock = True
            elif line.startswith('#') or line.startswith('@'):
                lines_prompt.append(prompt + line)
                prompt = second
            # Empty line = second prompt.
            elif line.rstrip() == '':
                lines_prompt.append((second + line).rstrip())
            elif line.startswith('  '):
                prompt = second
                lines_prompt.append(prompt + line)
                if not lock:
                    prompt = first
            else:
                lines_prompt.append(prompt + line)
                if not lock:
                    prompt = first

        return _to_code(lines_prompt) + '\n' + output.rstrip()


def create_prompt(prompt):
    """Create a prompt manager.

    Parameters
    ----------

    prompt : str or class driving from BasePromptManager
        The prompt name ('python' or 'ipython') or a custom PromptManager
        class.

    """
    if prompt is None:
        prompt = 'python'
    if prompt == 'python':
        prompt = PythonPromptManager
    elif prompt == 'ipython':
        prompt = IPythonPromptManager
    # Instanciate the class.
    if isinstance(prompt, BasePromptManager):
        return prompt
    else:
        return prompt()

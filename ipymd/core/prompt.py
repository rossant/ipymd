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
    return '\n'.join(line.rstrip() for line in lines if line.rstrip())


def _add_line_prefix(lines, prefix):
    return [prefix + line for line in lines]


def _template_to_regex(template):
    regex = template
    regex = regex.replace('{n}', '\d+')
    # Escape special characters.
    for char in '{}[]()+*?':
        regex = regex.replace(char, '\\' + char)
    return regex


class BasePromptManager(object):
    input_prompt_template = ''  # may contain {n} for the input number
    output_prompt_template = ''

    def __init__(self):
        # Compile the prompt regexes.
        self._input_prompt_regex = _template_to_regex(
            self.input_prompt_template)
        self._output_prompt_regex = _template_to_regex(
            self.output_prompt_template)
        self.reset()

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

    @property
    def input_prompt_regex(self):
        return self._input_prompt_regex

    @property
    def output_prompt_regex(self):
        return self._output_prompt_regex

    def start_with_regex(self, line, regex):
        if not regex.startswith('^'):
            regex = '^' + regex
        reg = re.compile(regex)
        return reg.match(line)

    def split_input_output(self, text):
        lines = _to_lines(text)
        i = 0
        for line in lines:
            if not self.start_with_regex(line, self.output_prompt_regex):
                i += 1
            else:
                break
        return lines[:i], lines[i:]

    def from_cell(self, input, output):
        raise NotImplementedError()

    def to_cell(self, code):
        raise NotImplementedError()


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

        return input.rstrip() + '\n' + output.rstrip()


#------------------------------------------------------------------------------
# IPython prompt manager
#------------------------------------------------------------------------------

class IPythonPromptManager(BasePromptManager):
    input_prompt_template = 'In [{n}]: '
    output_prompt_template = 'Out [{n}]: '

    def _add_prompt(self, lines, prompt):
        lines[:1] = _add_line_prefix(lines[:1], prompt)
        lines[1:] = _add_line_prefix(lines[1], ' ' * len(prompt))
        return lines

    def from_cell(self, input, output=None):
        input_l = _to_lines(input)
        output_l = _to_lines(output)

        input_l = self._add_prompt(input_l, self._input_prompt())
        output_l = self._add_prompt(output_l, self._output_prompt())

        input_p = _to_code(input_l)
        output_p = _to_code(output_l)

        self._number += 1

        return input_p + '\n' + output_p

    def to_cell(self, text):
        input_l, output_l = self.split_input_output(text)

        m = self.start_with_regex(input_l[0], self.input_prompt_regex)
        assert m
        input_prompt = m.group(0)
        n_in = len(input_prompt)
        input_l = [line[n_in:] for line in input_l]

        m = self.start_with_regex(output_l[0], self.output_prompt_regex)
        assert m
        output_prompt = m.group(0)
        n_out = len(output_prompt)
        output_l = [line[n_out:] for line in output_l]

        input = _to_code(input_l)
        output = _to_code(output_l)

        return input, output

#!/usr/bin/env python

from __future__ import unicode_literals
from __future__ import print_function

from os.path import expanduser

from prompt_toolkit import HTML
from prompt_toolkit import prompt
from prompt_toolkit import PromptSession
from prompt_toolkit import print_formatted_text as printc

from interpreter import PythonInterpreter
from interactive import user_functions

from prompt_toolkit.styles import Style
from prompt_toolkit.history import FileHistory
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory

banner = "POETS Client (pcli) v0.1"

usage="""POETS Client (pcli) v0.1

Usage:
  pcli.py [options]

Options:
  -n --nocolor   Disable terminal colors.

"""

styles = {
    "prompt": "ansiblue bold",
    "error": "gray"
}

ps1 = '<prompt>pcli> </prompt>'

syntactic_sugar = {
    "time on": "_timer = True",
    "time off": "_timer = False",
    "engines": "engines()"
}


def create_prompt(history_file):
    """Create a function that prompts the user for a command."""
    style = Style.from_dict(styles)
    history = FileHistory(history_file)
    session = PromptSession(style=style, history=history)
    ps1_html = HTML(ps1)
    auto_suggest = AutoSuggestFromHistory()
    def prompt():
        return session.prompt(ps1_html, auto_suggest=auto_suggest)
    return prompt


def main():

    context_file = expanduser("~/.pcli_context")
    history_file = expanduser("~/.pcli_history")

    prompt = create_prompt(history_file)
    interpreter = PythonInterpreter(user_functions, context_file)
    printc(banner)

    while True:
        try:
            command = prompt()
        except KeyboardInterrupt:
            continue
        except EOFError:
            break
        command = syntactic_sugar.get(command, command)
        result = interpreter.eval(command)
        print(result, end="")


if __name__ == '__main__':
    main()

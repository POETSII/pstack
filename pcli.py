#!/usr/bin/env python

from __future__ import unicode_literals
from __future__ import print_function

from os.path import expanduser

from prompt_toolkit import HTML
from prompt_toolkit import prompt
from prompt_toolkit import PromptSession
from prompt_toolkit import print_formatted_text as printc

import json

from files import read_file
from files import read_json

from interpreter import PythonInterpreter

from prompt_toolkit.styles import Style
from prompt_toolkit.history import FileHistory
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory

banner = "POETS Client (pcli) v0.1"

styles = {
    "prompt": "ansigreen bold",
    "error": "gray"
}

ps1 = '<prompt>pcli> </prompt>'

syntactic_sugar = {
    "ls": "ls()"
}

def run_job(redis_cl, xml, region_map):
    job_queue = "cli1"
    job = {"xml": xml, "region_map": region_map, "result_queue": job_queue}
    job_str = json.dumps(job)
    redis_cl.delete(job_queue)
    redis_cl.rpush("jobs", job_str)
    result_str = redis_cl.blpop(job_queue)[1]
    result = json.loads(result_str)
    return result


def run(xml_file, region_map_file):
    import redis
    redis_cl = redis.StrictRedis()
    xml = read_file(xml_file)
    region_map = read_json(region_map_file)
    result = run_job(redis_cl, xml, region_map)
    return result


def create_prompt(history_file):
    """Create function that prompts user for a command."""
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

    functions = [run]
    interpreter = PythonInterpreter(functions, context_file)

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

#!/usr/bin/env python

from __future__ import unicode_literals

from os.path import expanduser

from prompt_toolkit import HTML
from prompt_toolkit import prompt
from prompt_toolkit import PromptSession
from prompt_toolkit import print_formatted_text as printc

import json

from files import read_file
from files import read_json

from prompt_toolkit.styles import Style
from prompt_toolkit.history import FileHistory
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory

banner = "POETS Client (pcli) v0.1"

styles = {
    "prompt": "ansigreen bold",
    "error": "gray"
}

ps1 = '<prompt>pcli> </prompt>'


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


def main():
    printc(banner)
    style = Style.from_dict(styles)
    history = FileHistory(expanduser("~/.pcli_history"))
    session = PromptSession(style=style, history=history)
    ps1_html = HTML(ps1)
    auto_suggest = AutoSuggestFromHistory()
    while True:
        try:
            command = session.prompt(ps1_html, auto_suggest=auto_suggest)
        except KeyboardInterrupt:
            continue
        except EOFError:
            break
        args = command.split()
        if not args:
            continue
        if args[0] == "sim":
            xml_file, region_map_file = ("tests/ring-oscillator-01.xml", "tmp/map1.json")
            result = run(xml_file, region_map_file)
            print(json.dumps(result, indent=4))
            continue
        printc(HTML("<error>Unknown command</error>"), style=style)


if __name__ == '__main__':
    main()

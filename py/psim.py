#!/usr/bin/env python

from __future__ import print_function

import json
import docopt

from files import is_file
from files import read_file
from files import read_json
from schema import Schema
from simulator import simulate


usage="""POETS Simulator (PSIM) v0.1

Usage:
  psim.py [options] <app.xml>

Options:
  -l --level=<n>        Specify log messages verbosity [default: 1].
  -q --quiet            Suppress in-simulation outputs.
  -r --result           Print simulation result as JSON object.
  -t --temp=<dir>       Specify simulation file directory [default: /tmp].
  -d --debug            Print debug information.

"""


def psim(xml_input, rmap={}, options={}):
    """Simulate POETS XML.

    Arguments:
      - xml_input  (str) : an XML file or string.
      - rmap      (dict) : device region map [optional].
      - options   (dict) : simulation options [optional].

    See docstring of simulator.simulate for simulation options documentation.

    Return:
      - result (dict) : simulation result.

    """
    xml = read_file(xml_input) if is_file(xml_input) else xml_input
    schema = Schema(xml, rmap)
    result = simulate(schema, options)
    return result


def main():
    args = docopt.docopt(usage, version="v0.1")
    options = {
        "debug": args["--debug"],
        "quiet": args["--quiet"],
        "level": int(args["--level"]),
        "temp_dir": args["--temp"],
        "printer": print
    }
    result = psim(args["<app.xml>"], {}, options)
    if args["--result"]:
        print(json.dumps(result))


if __name__ == '__main__':
    main()

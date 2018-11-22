#!/usr/bin/env python

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
  -d --debug            Print debug information.
  -l --level=<n>        Specify log messages verbosity [default: 1].
  -t --temp=<dir>       Specify simulation file directory [default: /tmp].
  -m --map=<file.json>  Load device region map from file.
  -r --result           Print simulation result as JSON object.
  -q --quiet            Suppress all outputs (except --result).

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
    rmap = read_json(args["--map"]) if args["--map"] else {}
    options = {
        "debug": args["--debug"],
        "quiet": args["--quiet"],
        "level": int(args["--level"]),
        "temp_dir": args["--temp"]
    }
    result = psim(args["<app.xml>"], rmap, options)
    if args["--result"]:
        print(json.dumps(result))


if __name__ == '__main__':
    main()

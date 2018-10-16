#!/usr/bin/env python

import json
import docopt

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
  -m --map=<file.json>  Load device map from file.
  -r --result           Print simulation result as JSON object.
  -q --quiet            Suppress all outputs (except --result).

"""


def psim(xml, region_map, options):
    """Simulate POETS XML (thin wrapper around simulator.simulate)."""
    schema = Schema(xml, region_map)
    result = simulate(schema, options)
    return result


def main():
    args = docopt.docopt(usage, version="v0.1")
    xml = read_file(args["<app.xml>"])
    region_map = read_json(args["--map"]) if args["--map"] else {}
    options = {
        "debug": args["--debug"],
        "quiet": args["--quiet"],
        "level": int(args["--level"]),
        "temp_dir": args["--temp"]
    }
    result = psim(xml, region_map, options)
    if args["--result"]:
        print(json.dumps(result))


if __name__ == '__main__':
    main()

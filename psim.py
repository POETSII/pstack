#!/usr/bin/env python

import json
import docopt

from files import read_file
from files import read_json
from parser import parse_poets_xml
from generator import generate_code
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


def psim(xml, region_map={}, regions=[], options={}, quiet=False,
         temp_dir="/tmp", force_socat=False, redis_hostport="localhost:6379"):
    """Simulate POETS application.

    Arguments:
      - region_map  (dict) : map device_name (str) -> region (int)
      - regions     (list) : list of regions to simulate (falsey for all)
      - options     (dict) : additional configuration options, see below
      - quiet       (bool) : suppress simulation output
      - temp_dir    (str)  : temp directory for simulation file
      - force_socat (bool) : force using socat (for single-region simulations)

    Fields of 'options' dictionary:
      - debug       (bool) : print simulator debug information
      - level       (int)  : log message verbosity level

    Returns:
      - result      (dict) : simulation results
    """
    markup = parse_poets_xml(xml)
    code, all_regions = generate_code(markup, options, region_map)
    result = simulate(code, quiet, regions or all_regions, force_socat,
                      temp_dir, redis_hostport)
    return result


def main():
    args = docopt.docopt(usage, version="v0.1")
    result = psim(
        xml=read_file(args["<app.xml>"]),
        region_map=read_json(args["--map"]) if args["--map"] else {},
        options={"debug": args["--debug"], "level": int(args["--level"])},
        quiet=args["--quiet"],
        temp_dir=args["--temp"])
    if args["--result"]:
        print(json.dumps(result))


if __name__ == '__main__':
    main()

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


def main():
    args = docopt.docopt(usage, version="v0.1")
    markup = parse_poets_xml(read_file(args["<app.xml>"]))
    options = {"debug": args["--debug"], "level": int(args["--level"])}
    region_map = read_json(args["--map"]) if args["--map"] else {}
    code, nregions = generate_code(markup, options, region_map)
    result = simulate(code, args["--quiet"], nregions, args["--temp"])
    if args["--result"]:
        print(json.dumps(result))


if __name__ == '__main__':
    main()

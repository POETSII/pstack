import json
import docopt

from files import read_json
from parser import read_poets_xml
from generator import generate_code
from simulator import simulate
from simulator import simulate_raw


usage="""POETS Simulator (PSIM) v0.1

Usage:
  psim.py [options] <app.xml>

Options:
  -d --debug            Print debug information.
  -l --level=<n>        Specify log messages verbosity [default: 1].
  -t --temp=<dir>       Specify simulation file directory [default: /tmp].
  -g --region=<n>       Specify simulation region [default: 0].
  -m --map=<file.json>  Load device map from file.
  -r --result           Print simulation result as JSON object.
  -q --quiet            Suppress all outputs (except --result).

"""


def main():
    args = docopt.docopt(usage, version="v0.1")
    markup = read_poets_xml(args["<app.xml>"])
    region = int(args["--region"])
    options = {"debug": args["--debug"], "level": int(args["--level"])}
    region_map = read_json(args["--map"]) if args["--map"] else {}
    code = generate_code(markup, options, region=region, region_map=region_map)
    simulate_raw(code, temp_dir=args["--temp"])
    return

    result = simulate(code, quiet=args["--quiet"], temp_dir=args["--temp"])
    if args["--result"]:
        print(json.dumps(result))


if __name__ == '__main__':
    main()

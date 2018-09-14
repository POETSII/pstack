import json
import docopt

from parser import read_poets_xml
from generator import generate_code
from simulator import simulate
from simulator import simulate_raw


usage="""POETS Simulator (PSIM) v0.1

Usage:
  psim.py [options] <app.xml>

Options:
  -d --debug       Print debug information.
  -l --level=<n>   Specify log messages verbosity [default: 1].
  -t --temp=<dir>  Specify simulation file directory [default: /tmp].
  -r --result      Print simulation result as JSON object.
  -q --quiet       Suppress all outputs (except --result).

"""


def main():
    args = docopt.docopt(usage, version="v0.1")
    markup = read_poets_xml(args["<app.xml>"])
    options = {"debug": args["--debug"], "level": int(args["--level"])}

    region = 1
    region_map = {"nx": 1}
    # region_map = {}
    code = generate_code(markup, options, region=region, region_map=region_map)
    simulate_raw(code, temp_dir=args["--temp"])
    return

    result = simulate(code, quiet=args["--quiet"], temp_dir=args["--temp"])
    if args["--result"]:
        print(json.dumps(result))


if __name__ == '__main__':
    main()

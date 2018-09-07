import json
import docopt

from parser import read_poets_xml
from generator import generate_code
from simulator import simulate


usage="""POETS Simulator (PSIM) v0.1

Usage:
  psim.py [options] <app.xml>

Options:
  -d --debug       Print simulator debug information.
  -l --level=<n>   Specify log messages verbosity [default: 1].
  -r --result      Print simulation results as JSON object.
  -t --temp=<dir>  Specify simulation file directory [default: /tmp].
  -q --quiet       Suppress all outputs.

"""


def main():
    args = docopt.docopt(usage, version="v0.1")
    markup = read_poets_xml(args["<app.xml>"])
    options = {"debug": args["--debug"],
               "level": int(args["--level"])}
    code = generate_code(markup, options)
    result = simulate(code, quiet=args["--quiet"], temp_dir=args["--temp"])
    if args["--result"]:
        print(json.dumps(result))


if __name__ == '__main__':
    main()

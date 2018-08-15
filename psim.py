import docopt

from parser import read_poets_xml
from generator import generate_code
from simulator import simulate


usage="""POETS Markup Simulator (PSIM) v0.1

Usage:
  psim.py [options] <app.xml>

Options:
  --debug, -d  Print debug information.

"""


def main():
    args = docopt.docopt(usage, version="v0.1")
    markup = read_poets_xml(args["<app.xml>"])
    options = {"debug": args["--debug"]}
    code = generate_code(markup, options)
    simulate(code)


if __name__ == '__main__':
    main()

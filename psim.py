import docopt

from parser import read_poets_xml
from generator import generate_code
from simulator import simulate


usage="""POETS Markup Simulation (PSIM) v0.1

Usage:
  psim.py <app.xml>

"""


def main():

    args = docopt.docopt(usage, version="v0.1")
    markup = read_poets_xml(args["<app.xml>"])
    code = generate_code(markup)

    simulate(code)


if __name__ == '__main__':
    main()

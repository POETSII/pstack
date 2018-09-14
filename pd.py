import docopt


usage="""POETS Daemon (PD) v0.1

Usage:
  pd.py [options]

Options:
  -w --workers=<n>   Specify number of POETS workers [default: 2].
  -r --redis=<host>  Specify Redis host [default: localhost:6379].
  -q --quiet         Suppress all outputs.

"""


def main():
    args = docopt.docopt(usage, version="v0.1")
    print args


if __name__ == '__main__':
    main()

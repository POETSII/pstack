import os
import json
import docopt

from parser import read_poets_xml
from generator import generate_code

usage="""POETS Markup Simulation (PSIM) v0.1

Usage:
  psim.py [options] <app.xml>

Options:
  -n --norun          Do not execute generated code.
  -o --output=<file>  Specify temporary source code file.
"""


def write_file(file, content):
    """Write string to file."""
    with open(file, 'w') as fid:
        fid.write(content)


def compile_gpp(source_file, output):
    """Compile c++ source file."""

    cmd = "g++ -o %s %s" % (output, source_file)
    exit_code = os.system(cmd)

    if exit_code is not 0:
        raise Exception("Compilation failed (%s)" % source_file)


def main():

    args = docopt.docopt(usage, version="v0.1")

    xml_file = 'tmp/output.xml'
    template_file = 'main.cpp'
    temp_obj_file = "/tmp/psim.exe"
    temp_code_file = args["--output"] or "/tmp/psim.cpp"

    markup = read_poets_xml(args["<app.xml>"])
    code = generate_code(template_file, markup)

    write_file(temp_code_file, code)

    if args["--norun"]:
        return  # nothing else to do

    compile_gpp(temp_code_file, temp_obj_file)

    os.system(temp_obj_file)


if __name__ == '__main__':
    main()
